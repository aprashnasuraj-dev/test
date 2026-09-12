"""Stateful orchestration for the seven-stage ENS audit pipeline."""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Protocol
from uuid import UUID

from ens_audit.config import ACTIVE_UPSTREAM_COMMIT, DATABASE_PATH
from ens_audit.downloader import download_all_repos
from ens_audit.models import Asset, AuditReport, Finding
from ens_audit.pipeline.stage_deps import DependencyStage
from ens_audit.pipeline.stage_fuzz import FuzzStage
from ens_audit.pipeline.stage_known_filter import KnownIssueFilterStage
from ens_audit.pipeline.stage_report import ReportStage
from ens_audit.pipeline.stage_sast import SASTStage
from ens_audit.pipeline.stage_secrets import SecretStage
from ens_audit.pipeline.stage_symbolic import SymbolicStage
from ens_audit.pipeline.store import AnalysisStore

ProgressCallback = Callable[[str, str, int, int], None]
LogCallback = Callable[[str], None]


class AnalysisStage(Protocol):
    """Structural interface implemented by every per-asset analysis stage."""

    async def run(self, asset: Asset) -> list[Finding]:
        """Analyze one validated asset and return normalized findings."""


class PipelineCancelled(RuntimeError):
    """Raised when a cooperative pipeline cancellation is observed."""


class PipelineControl:
    """Thread-safe pause/resume/cancel state shared with a GUI worker."""

    def __init__(self) -> None:
        self._resume_gate = threading.Event()
        self._resume_gate.set()
        self._cancelled = threading.Event()

    def pause(self) -> None:
        """Pause before the next stage boundary without terminating an in-flight scanner."""

        self._resume_gate.clear()

    def resume(self) -> None:
        """Allow execution to proceed past the next stage boundary."""

        self._resume_gate.set()

    def cancel(self) -> None:
        """Request cancellation at the next cooperative boundary."""

        self._cancelled.set()
        self._resume_gate.set()

    def reset(self) -> None:
        """Reset control state for a new or retried run."""

        self._cancelled.clear()
        self._resume_gate.set()

    async def checkpoint(self) -> None:
        """Wait while paused and raise if cancellation was requested."""

        await asyncio.to_thread(self._resume_gate.wait)
        if self._cancelled.is_set():
            raise PipelineCancelled("audit cancelled")


class PipelineOrchestrator:
    """Execute and checkpoint the complete audit workflow.

    Security invariant: only downloader-validated assets enter analyzers; failed stages are
    checkpointed as failed, remain eligible for resume, and never cause shell fallback.
    """

    STAGES = ("sast", "symbolic", "fuzz", "deps", "secrets", "known_filter", "report")
    ANALYSIS_STAGES = ("sast", "symbolic", "fuzz", "deps", "secrets")

    def __init__(
        self,
        *,
        store: AnalysisStore | None = None,
        strict: bool = False,
        progress: ProgressCallback | None = None,
        logger: LogCallback | None = None,
        control: PipelineControl | None = None,
    ) -> None:
        """Initialize pipeline stages and cooperative execution state."""

        self.store = store or AnalysisStore(DATABASE_PATH)
        self.strict = strict
        self.progress = progress
        self.logger = logger
        self.control = control or PipelineControl()
        self.current_run_id: UUID | None = None
        rules = Path(__file__).resolve().parents[1] / "rules" / "ens-custom.yaml"
        self.stage_sast = SASTStage(rules)
        self.stage_symbolic = SymbolicStage()
        self.stage_fuzz = FuzzStage()
        self.stage_deps = DependencyStage()
        self.stage_secrets = SecretStage()
        self.stage_known_filter = KnownIssueFilterStage()
        self.stage_report = ReportStage()

    async def run_full_audit(self) -> AuditReport:
        """Download the pinned source and execute all seven stages end to end."""

        return await self.run_selected(list(self.ANALYSIS_STAGES))

    async def run_selected(self, stages: list[str]) -> AuditReport:
        """Run a validated subset of analysis stages, then filter and report."""

        selected = self._validate_stage_selection(stages)
        self.control.reset()
        assets = await download_all_repos()
        run_id = self.store.begin_run(ACTIVE_UPSTREAM_COMMIT, selected)
        self.current_run_id = run_id
        return await self._run_assets(run_id, assets, selected_stages=selected)

    async def resume(self, run_id: UUID) -> AuditReport:
        """Resume exactly the source commit and analysis stages recorded for a prior run.

        Security invariant: source revision drift is rejected before repository acquisition, so
        findings from different commits can never be merged into one audit run.
        """

        stored_commit = self.store.run_commit(run_id)
        if stored_commit != ACTIVE_UPSTREAM_COMMIT:
            raise RuntimeError(
                "cannot resume audit run after source commit changed: "
                f"stored={stored_commit} active={ACTIVE_UPSTREAM_COMMIT}"
            )
        selected = self._validate_stage_selection(list(self.store.run_analysis_stages(run_id)))
        self.control.reset()
        self.current_run_id = run_id
        assets = await download_all_repos()
        return await self._run_assets(run_id, assets, selected_stages=selected)

    async def retry_failed(self) -> AuditReport:
        """Retry incomplete stages for the current run identifier."""

        if self.current_run_id is None:
            raise RuntimeError("no audit run is available to retry")
        return await self.resume(self.current_run_id)

    async def _run_assets(
        self,
        run_id: UUID,
        assets: list[Asset],
        *,
        selected_stages: tuple[str, ...] | None = None,
    ) -> AuditReport:
        """Execute selected analyzers, filter known issues, and generate reports."""

        selected = selected_stages or self.ANALYSIS_STAGES
        results: dict[str, list[Finding]] = {}
        total_steps = len(assets) * (len(selected) + 1) + 1
        current = 0

        for asset in assets:
            findings: list[Finding] = []
            completed = self.store.completed_stages(run_id, asset.name)
            for stage_name, stage in self._analysis_stages(selected):
                await self.control.checkpoint()
                current += 1
                self._emit_progress(asset.name, stage_name, current, total_steps)
                if stage_name in completed:
                    self._log(f"skip {asset.name}:{stage_name}; checkpoint already complete")
                    continue
                stage_findings, succeeded = await self._run_stage(stage_name, stage, asset)
                findings.extend(stage_findings)
                self.store.save_stage(
                    run_id,
                    asset.name,
                    stage_name,
                    stage_findings,
                    succeeded=succeeded,
                )
            persisted = [
                finding
                for finding in self.store.load_findings(run_id)
                if finding.asset == asset.name
            ]
            if persisted:
                findings = self._dedupe_by_id([*persisted, *findings])

            await self.control.checkpoint()
            current += 1
            self._emit_progress(asset.name, "known_filter", current, total_steps)
            filtered = await self.stage_known_filter.run(findings)
            self.store.save_stage(
                run_id,
                asset.name,
                "known_filter",
                filtered,
                succeeded=True,
            )
            results[asset.name] = filtered

        await self.control.checkpoint()
        current += 1
        self._emit_progress("all", "report", current, total_steps)
        report = await self.stage_report.generate(results)
        self.store.save_stage(run_id, "__all__", "report", [], succeeded=True)
        return report

    def _analysis_stages(
        self,
        selected: tuple[str, ...],
    ) -> tuple[tuple[str, AnalysisStage], ...]:
        """Return selected analyzer stages in mandatory dependency order."""

        available: tuple[tuple[str, AnalysisStage], ...] = (
            ("sast", self.stage_sast),
            ("symbolic", self.stage_symbolic),
            ("fuzz", self.stage_fuzz),
            ("deps", self.stage_deps),
            ("secrets", self.stage_secrets),
        )
        selected_set = set(selected)
        return tuple(item for item in available if item[0] in selected_set)

    @classmethod
    def _validate_stage_selection(cls, stages: list[str]) -> tuple[str, ...]:
        """Validate and canonicalize caller-selected analysis stages."""

        requested = {stage.strip().lower() for stage in stages if stage.strip()}
        unknown = requested - set(cls.ANALYSIS_STAGES)
        if unknown:
            raise ValueError(f"unknown analysis stages: {', '.join(sorted(unknown))}")
        if not requested:
            raise ValueError("at least one analysis stage must be selected")
        return tuple(stage for stage in cls.ANALYSIS_STAGES if stage in requested)

    async def _run_stage(
        self,
        name: str,
        stage: AnalysisStage,
        asset: Asset,
    ) -> tuple[list[Finding], bool]:
        """Run one analyzer and enforce the unified finding schema at the stage boundary."""

        try:
            findings = await stage.run(asset)
            if not isinstance(findings, list):
                raise TypeError(f"{name} returned {type(findings).__name__}; expected list[Finding]")
            invalid = [type(finding).__name__ for finding in findings if not isinstance(finding, Finding)]
            if invalid:
                raise TypeError(
                    f"{name} returned non-Finding result(s): {', '.join(sorted(set(invalid)))}"
                )
            self._log(f"complete {asset.name}:{name}; findings={len(findings)}")
            return findings, True
        except PipelineCancelled:
            raise
        except Exception as exc:
            self._log(f"failed {asset.name}:{name}; {type(exc).__name__}: {exc}")
            if self.strict:
                raise
            return [], False

    @staticmethod
    def _dedupe_by_id(findings: list[Finding]) -> list[Finding]:
        """Keep the latest representation for each immutable finding id."""

        by_id = {finding.id: finding for finding in findings}
        return list(by_id.values())

    def _emit_progress(self, asset: str, stage: str, current: int, total: int) -> None:
        """Emit progress data to the GUI callback when configured."""

        if self.progress is not None:
            self.progress(asset, stage, current, total)

    def _log(self, message: str) -> None:
        """Emit a pipeline log line without evaluating its contents."""

        if self.logger is not None:
            self.logger(message)

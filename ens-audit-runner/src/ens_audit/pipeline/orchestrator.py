"""Stateful orchestration for the seven-stage ENS audit pipeline."""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Callable
from pathlib import Path
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


class PipelineCancelled(RuntimeError):
    """Raised when a cooperative pipeline cancellation is observed."""


class PipelineControl:
    """Thread-safe pause/resume/cancel state shared with a GUI worker.

    Security invariant: control methods affect only stage-boundary scheduling and never kill
    arbitrary processes or threads asynchronously.
    """

    def __init__(self) -> None:
        """Initialize the pipeline in running, non-cancelled state.

        Security invariant: execution starts unpaused and requires an explicit cancel request
        before cancellation can occur.
        """

        self._resume_gate = threading.Event()
        self._resume_gate.set()
        self._cancelled = threading.Event()

    def pause(self) -> None:
        """Pause before the next stage boundary.

        Security invariant: an in-flight external scanner is not force-terminated.
        """

        self._resume_gate.clear()

    def resume(self) -> None:
        """Allow execution to proceed past the next stage boundary.

        Security invariant: resume changes only the cooperative gate state.
        """

        self._resume_gate.set()

    def cancel(self) -> None:
        """Request cancellation at the next cooperative boundary.

        Security invariant: cancellation unblocks a paused waiter but does not terminate
        unrelated processes or threads.
        """

        self._cancelled.set()
        self._resume_gate.set()

    def reset(self) -> None:
        """Reset control state for a new or retried run.

        Security invariant: stale cancellation state cannot leak into a subsequent run.
        """

        self._cancelled.clear()
        self._resume_gate.set()

    async def checkpoint(self) -> None:
        """Wait while paused and raise if cancellation was requested.

        Security invariant: blocking occurs in a worker thread so the asyncio loop remains
        responsive.
        """

        await asyncio.to_thread(self._resume_gate.wait)
        if self._cancelled.is_set():
            raise PipelineCancelled("audit cancelled")


class PipelineOrchestrator:
    """Execute and checkpoint the complete audit workflow.

    Security invariant: only downloader-validated assets enter analyzers; failed stages are
    checkpointed as failed, remain eligible for resume, and never cause shell fallback.
    """

    STAGES = ("sast", "symbolic", "fuzz", "deps", "secrets", "known_filter", "report")

    def __init__(
        self,
        *,
        store: AnalysisStore | None = None,
        strict: bool = False,
        progress: ProgressCallback | None = None,
        logger: LogCallback | None = None,
        control: PipelineControl | None = None,
    ) -> None:
        """Initialize pipeline stages and cooperative execution state.

        Security invariant: analyzer instances are fixed at construction and operate only on
        downloader-validated assets.
        """

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
        """Download the pinned source and execute all seven stages end to end.

        Security invariant: every new run begins with a reset cooperative-control state and a
        freshly recorded immutable commit identifier.
        """

        self.control.reset()
        assets = await download_all_repos()
        run_id = self.store.begin_run(ACTIVE_UPSTREAM_COMMIT)
        self.current_run_id = run_id
        return await self._run_assets(run_id, assets)

    async def resume(self, run_id: UUID) -> AuditReport:
        """Resume a prior run, skipping only successful per-asset checkpoints.

        Security invariant: resume uses the caller-supplied UUID only as a parameterized SQLite
        key and still reacquires downloader-validated assets.
        """

        self.control.reset()
        self.current_run_id = run_id
        assets = await download_all_repos()
        return await self._run_assets(run_id, assets)

    async def retry_failed(self) -> AuditReport:
        """Retry incomplete stages for the current run identifier.

        Security invariant: a retry can only target the orchestrator's own current run.
        """

        if self.current_run_id is None:
            raise RuntimeError("no audit run is available to retry")
        return await self.resume(self.current_run_id)

    async def _run_assets(self, run_id: UUID, assets: list[Asset]) -> AuditReport:
        """Execute analyzer stages, filter known issues, and generate reports."""

        results: dict[str, list[Finding]] = {}
        total_steps = len(assets) * 6 + 1
        current = 0

        for asset in assets:
            findings: list[Finding] = []
            completed = self.store.completed_stages(run_id, asset.name)
            for stage_name, stage in self._analysis_stages():
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
                finding for finding in self.store.load_findings(run_id) if finding.asset == asset.name
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

    def _analysis_stages(self) -> tuple[tuple[str, object], ...]:
        """Return analyzer stages in mandatory dependency order.

        Security invariant: dependency order is fixed in code and cannot be supplied by scan
        output.
        """

        return (
            ("sast", self.stage_sast),
            ("symbolic", self.stage_symbolic),
            ("fuzz", self.stage_fuzz),
            ("deps", self.stage_deps),
            ("secrets", self.stage_secrets),
        )

    async def _run_stage(
        self,
        name: str,
        stage: object,
        asset: Asset,
    ) -> tuple[list[Finding], bool]:
        """Run one analyzer and return findings plus an explicit success state.

        Security invariant: an isolated exception can never be represented as a successful
        empty scan.
        """

        try:
            run_method = getattr(stage, "run")
            findings: list[Finding] = await run_method(asset)
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
        """Keep the latest representation for each immutable finding id.

        Security invariant: deduplication keys use generated UUIDs rather than untrusted text.
        """

        by_id = {finding.id: finding for finding in findings}
        return list(by_id.values())

    def _emit_progress(self, asset: str, stage: str, current: int, total: int) -> None:
        """Emit progress data to the GUI callback when configured.

        Security invariant: callbacks receive scalar progress metadata only.
        """

        if self.progress is not None:
            self.progress(asset, stage, current, total)

    def _log(self, message: str) -> None:
        """Emit a pipeline log line without evaluating its contents.

        Security invariant: log callbacks receive inert strings only.
        """

        if self.logger is not None:
            self.logger(message)

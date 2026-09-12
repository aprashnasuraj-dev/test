"""Stateful orchestration for the seven-stage ENS audit pipeline."""

from __future__ import annotations

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


class PipelineOrchestrator:
    """Execute and checkpoint the complete audit workflow.

    Security invariant: only downloader-validated assets enter analyzers; failed stages do not
    mutate another stage's checkpoint and never cause shell fallback.
    """

    STAGES = ("sast", "symbolic", "fuzz", "deps", "secrets", "known_filter", "report")

    def __init__(
        self,
        *,
        store: AnalysisStore | None = None,
        strict: bool = False,
        progress: ProgressCallback | None = None,
        logger: LogCallback | None = None,
    ) -> None:
        self.store = store or AnalysisStore(DATABASE_PATH)
        self.strict = strict
        self.progress = progress
        self.logger = logger
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

        assets = await download_all_repos()
        run_id = self.store.begin_run(ACTIVE_UPSTREAM_COMMIT)
        return await self._run_assets(run_id, assets)

    async def resume(self, run_id: UUID) -> AuditReport:
        """Resume a prior run, skipping successful per-asset checkpoints."""

        assets = await download_all_repos()
        return await self._run_assets(run_id, assets)

    async def _run_assets(self, run_id: UUID, assets: list[Asset]) -> AuditReport:
        """Execute analyzer stages, filter known issues, and generate reports."""

        results: dict[str, list[Finding]] = {}
        total_steps = len(assets) * 6 + 1
        current = 0

        for asset in assets:
            findings: list[Finding] = []
            completed = self.store.completed_stages(run_id, asset.name)
            for stage_name, stage in self._analysis_stages():
                current += 1
                self._emit_progress(asset.name, stage_name, current, total_steps)
                if stage_name in completed:
                    self._log(f"skip {asset.name}:{stage_name}; checkpoint already complete")
                    continue
                stage_findings = await self._run_stage(stage_name, stage, asset)
                findings.extend(stage_findings)
                self.store.save_stage(
                    run_id,
                    asset.name,
                    stage_name,
                    stage_findings,
                    succeeded=True,
                )
            persisted = [
                finding for finding in self.store.load_findings(run_id) if finding.asset == asset.name
            ]
            if persisted:
                findings = self._dedupe_by_id([*persisted, *findings])

            filtered = await self.stage_known_filter.run(findings)
            self.store.save_stage(
                run_id,
                asset.name,
                "known_filter",
                filtered,
                succeeded=True,
            )
            results[asset.name] = filtered

        current += 1
        self._emit_progress("all", "report", current, total_steps)
        report = await self.stage_report.generate(results)
        self.store.save_stage(run_id, "__all__", "report", [], succeeded=True)
        return report

    def _analysis_stages(self) -> tuple[tuple[str, object], ...]:
        """Return analyzer stages in mandatory dependency order."""

        return (
            ("sast", self.stage_sast),
            ("symbolic", self.stage_symbolic),
            ("fuzz", self.stage_fuzz),
            ("deps", self.stage_deps),
            ("secrets", self.stage_secrets),
        )

    async def _run_stage(self, name: str, stage: object, asset: Asset) -> list[Finding]:
        """Run one analyzer with exception isolation unless strict mode is enabled."""

        try:
            run_method = getattr(stage, "run")
            findings: list[Finding] = await run_method(asset)
            self._log(f"complete {asset.name}:{name}; findings={len(findings)}")
            return findings
        except Exception as exc:
            self._log(f"failed {asset.name}:{name}; {type(exc).__name__}: {exc}")
            if self.strict:
                raise
            return []

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

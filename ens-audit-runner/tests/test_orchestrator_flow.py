"""End-to-end orchestration tests using local state and fake analysis stages."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest

from ens_audit.models import Asset, AuditReport, Finding, Location, Severity
from ens_audit.pipeline.orchestrator import (
    PipelineCancelled,
    PipelineControl,
    PipelineOrchestrator,
)
from ens_audit.pipeline.store import AnalysisStore


def _finding(asset: Asset) -> Finding:
    """Build one deterministic orchestration finding."""

    return Finding(
        title="orchestrated finding",
        severity=Severity.MEDIUM,
        asset=asset.name,
        stage="sast",
        rule_id="orchestrator-test",
        root_cause="new_root_cause",
        location=Location("src/example.ts", 4),
        description="example",
        evidence="example",
    )


@pytest.mark.asyncio
async def test_pipeline_control_cancel_reset_and_resume() -> None:
    """Cooperative control unblocks cancellation and can be safely reset for a new run."""

    control = PipelineControl()
    control.pause()
    control.cancel()
    with pytest.raises(PipelineCancelled, match="audit cancelled"):
        await control.checkpoint()
    control.reset()
    control.pause()
    control.resume()
    await control.checkpoint()


def test_stage_selection_is_closed_and_canonical(tmp_path: Path) -> None:
    """Selection rejects unknown/empty input and preserves mandatory execution order."""

    orchestrator = PipelineOrchestrator(store=AnalysisStore(tmp_path / "audit.sqlite3"))
    assert orchestrator._validate_stage_selection(["deps", "SAST", "sast"]) == (
        "sast",
        "deps",
    )
    assert [name for name, _stage in orchestrator._analysis_stages(("deps", "sast"))] == [
        "sast",
        "deps",
    ]
    with pytest.raises(ValueError, match="unknown analysis stages"):
        orchestrator._validate_stage_selection(["arbitrary"])
    with pytest.raises(ValueError, match="at least one"):
        orchestrator._validate_stage_selection([" "])


@pytest.mark.asyncio
async def test_selected_run_persists_and_resume_skips_completed_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A resumed run reuses its successful checkpoint instead of re-running the analyzer."""

    asset_root = tmp_path / "asset"
    asset_root.mkdir()
    asset = Asset("manager", asset_root, "a" * 40)
    downloads = 0

    async def fake_download() -> list[Asset]:
        nonlocal downloads
        downloads += 1
        return [asset]

    monkeypatch.setattr("ens_audit.pipeline.orchestrator.download_all_repos", fake_download)
    progress: list[tuple[str, str, int, int]] = []
    logs: list[str] = []
    store = AnalysisStore(tmp_path / "audit.sqlite3")
    orchestrator = PipelineOrchestrator(
        store=store,
        progress=lambda *values: progress.append(values),
        logger=logs.append,
    )

    class Stage:
        calls = 0

        async def run(self, selected_asset: Asset) -> list[Finding]:
            self.calls += 1
            return [_finding(selected_asset)]

    class Filter:
        async def run(self, findings: list[Finding]) -> list[Finding]:
            return findings

    class Reporter:
        async def generate(self, results: dict[str, list[Finding]]) -> AuditReport:
            combined = tuple(item for values in results.values() for item in values)
            return AuditReport("a" * 40, combined, ("sast", "known_filter", "report"), tmp_path)

    stage = Stage()
    orchestrator.stage_sast = stage  # type: ignore[assignment]
    orchestrator.stage_known_filter = Filter()  # type: ignore[assignment]
    orchestrator.stage_report = Reporter()  # type: ignore[assignment]

    report = await orchestrator.run_selected(["sast"])
    run_id = orchestrator.current_run_id
    assert isinstance(run_id, UUID)
    assert len(report.findings) == 1
    assert stage.calls == 1
    assert store.completed_stages(run_id, "manager") == {"sast", "known_filter"}
    assert store.completed_stages(run_id, "__all__") == {"report"}

    resumed = await orchestrator.resume(run_id)
    assert len(resumed.findings) == 1
    assert stage.calls == 1
    assert downloads == 2
    assert any(message.startswith("skip manager:sast") for message in logs)
    assert ("all", "report") == progress[-1][:2]


@pytest.mark.asyncio
async def test_cancelled_stage_propagates(tmp_path: Path) -> None:
    """Pipeline cancellation is never downgraded into an ordinary failed analyzer."""

    orchestrator = PipelineOrchestrator(store=AnalysisStore(tmp_path / "audit.sqlite3"))
    asset = Asset("manager", tmp_path, "b" * 40)

    class CancelStage:
        async def run(self, _asset: Asset) -> list[Finding]:
            raise PipelineCancelled("stop")

    with pytest.raises(PipelineCancelled, match="stop"):
        await orchestrator._run_stage("sast", CancelStage(), asset)

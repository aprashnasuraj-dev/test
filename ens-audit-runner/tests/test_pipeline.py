"""Tests for pipeline persistence and stage isolation."""

from __future__ import annotations

from pathlib import Path

import pytest

from ens_audit.models import Asset, Finding, Location, Severity
from ens_audit.pipeline.orchestrator import PipelineOrchestrator
from ens_audit.pipeline.store import AnalysisStore


def _finding() -> Finding:
    """Build one normalized finding for persistence tests."""

    return Finding(
        title="Example finding",
        severity=Severity.MEDIUM,
        asset="manager",
        stage="sast",
        rule_id="example-rule",
        root_cause="example_root",
        location=Location("src/file.ts", 5),
        description="description",
        evidence="evidence",
    )


def test_store_round_trip_and_checkpoint(tmp_path: Path) -> None:
    """A committed stage preserves findings and becomes resumable."""

    store = AnalysisStore(tmp_path / "audit.sqlite3")
    run_id = store.begin_run("a" * 40)
    finding = _finding()
    store.save_stage(run_id, "manager", "sast", [finding], succeeded=True)

    assert store.completed_stages(run_id, "manager") == {"sast"}
    [loaded] = store.load_findings(run_id)
    assert loaded.to_dict() == finding.to_dict()


def test_failed_checkpoint_is_not_completed(tmp_path: Path) -> None:
    """A failed stage is persisted as retryable rather than completed."""

    store = AnalysisStore(tmp_path / "audit.sqlite3")
    run_id = store.begin_run("b" * 40)
    store.save_stage(run_id, "manager", "sast", [], succeeded=False)
    assert store.completed_stages(run_id, "manager") == set()


class _SuccessStage:
    async def run(self, asset: Asset) -> list[Finding]:
        """Return one deterministic finding."""

        del asset
        return [_finding()]


class _FailingStage:
    async def run(self, asset: Asset) -> list[Finding]:
        """Raise a deterministic analyzer failure."""

        del asset
        raise RuntimeError("scanner crashed")


@pytest.mark.asyncio
async def test_run_stage_reports_success(tmp_path: Path) -> None:
    """Successful analyzer execution returns findings with success=true."""

    orchestrator = PipelineOrchestrator(store=AnalysisStore(tmp_path / "audit.sqlite3"))
    asset = Asset("manager", tmp_path, "c" * 40)
    findings, succeeded = await orchestrator._run_stage("sast", _SuccessStage(), asset)
    assert succeeded is True
    assert len(findings) == 1


@pytest.mark.asyncio
async def test_run_stage_isolates_failure_when_not_strict(tmp_path: Path) -> None:
    """Non-strict mode returns a failed status instead of a false successful empty scan."""

    orchestrator = PipelineOrchestrator(store=AnalysisStore(tmp_path / "audit.sqlite3"))
    asset = Asset("manager", tmp_path, "d" * 40)
    findings, succeeded = await orchestrator._run_stage("sast", _FailingStage(), asset)
    assert findings == []
    assert succeeded is False


@pytest.mark.asyncio
async def test_run_stage_raises_in_strict_mode(tmp_path: Path) -> None:
    """Strict mode propagates analyzer failures to the caller."""

    orchestrator = PipelineOrchestrator(
        store=AnalysisStore(tmp_path / "audit.sqlite3"),
        strict=True,
    )
    asset = Asset("manager", tmp_path, "e" * 40)
    with pytest.raises(RuntimeError, match="scanner crashed"):
        await orchestrator._run_stage("sast", _FailingStage(), asset)

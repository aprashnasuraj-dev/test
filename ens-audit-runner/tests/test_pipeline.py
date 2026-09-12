"""Tests for pipeline persistence and stage isolation."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import uuid4

import pytest

from ens_audit.config import ACTIVE_UPSTREAM_COMMIT
from ens_audit.models import Asset, Finding, Location, Severity
from ens_audit.pipeline import orchestrator as orchestrator_module
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
    run_id = store.begin_run("a" * 40, ("sast", "deps"))
    finding = _finding()
    store.save_stage(run_id, "manager", "sast", [finding], succeeded=True)

    assert store.run_commit(run_id) == "a" * 40
    assert store.run_analysis_stages(run_id) == ("sast", "deps")
    assert store.completed_stages(run_id, "manager") == {"sast"}
    [loaded] = store.load_findings(run_id)
    assert loaded.to_dict() == finding.to_dict()


def test_failed_checkpoint_is_not_completed(tmp_path: Path) -> None:
    """A failed stage is persisted as retryable rather than completed."""

    store = AnalysisStore(tmp_path / "audit.sqlite3")
    run_id = store.begin_run("b" * 40)
    store.save_stage(run_id, "manager", "sast", [], succeeded=False)
    assert store.completed_stages(run_id, "manager") == set()


def test_legacy_database_is_migrated_with_full_stage_default(tmp_path: Path) -> None:
    """Pre-stage-selection databases must migrate without losing existing run rows."""

    database = tmp_path / "legacy.sqlite3"
    run_id = uuid4()
    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TABLE runs ("
            "id TEXT PRIMARY KEY, commit_sha TEXT NOT NULL, "
            "created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        connection.execute(
            "INSERT INTO runs(id, commit_sha) VALUES(?, ?)",
            (str(run_id), "c" * 40),
        )

    store = AnalysisStore(database)
    assert store.run_commit(run_id) == "c" * 40
    assert store.run_analysis_stages(run_id) == (
        "sast",
        "symbolic",
        "fuzz",
        "deps",
        "secrets",
    )


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
    asset = Asset("manager", tmp_path, "d" * 40)
    findings, succeeded = await orchestrator._run_stage("sast", _SuccessStage(), asset)
    assert succeeded is True
    assert len(findings) == 1


@pytest.mark.asyncio
async def test_run_stage_isolates_failure_when_not_strict(tmp_path: Path) -> None:
    """Non-strict mode returns a failed status instead of a false successful empty scan."""

    orchestrator = PipelineOrchestrator(store=AnalysisStore(tmp_path / "audit.sqlite3"))
    asset = Asset("manager", tmp_path, "e" * 40)
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
    asset = Asset("manager", tmp_path, "f" * 40)
    with pytest.raises(RuntimeError, match="scanner crashed"):
        await orchestrator._run_stage("sast", _FailingStage(), asset)


@pytest.mark.asyncio
async def test_resume_rejects_commit_drift_before_download(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A run from another revision must never be resumed against the active checkout."""

    store = AnalysisStore(tmp_path / "audit.sqlite3")
    run_id = store.begin_run("0" * 40, ("sast",))
    orchestrator = PipelineOrchestrator(store=store)
    called = False

    async def fake_download() -> list[Asset]:
        nonlocal called
        called = True
        return []

    monkeypatch.setattr(orchestrator_module, "download_all_repos", fake_download)

    with pytest.raises(RuntimeError, match="source commit changed"):
        await orchestrator.resume(run_id)
    assert called is False


@pytest.mark.asyncio
async def test_resume_uses_persisted_stage_selection(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Resume must not expand a selected-stage run into all analysis stages."""

    store = AnalysisStore(tmp_path / "audit.sqlite3")
    run_id = store.begin_run(ACTIVE_UPSTREAM_COMMIT, ("deps", "secrets"))
    orchestrator = PipelineOrchestrator(store=store)
    selected_seen: tuple[str, ...] | None = None

    async def fake_download() -> list[Asset]:
        return []

    async def fake_run_assets(
        actual_run_id: object,
        assets: list[Asset],
        *,
        selected_stages: tuple[str, ...] | None = None,
    ) -> object:
        nonlocal selected_seen
        assert actual_run_id == run_id
        assert assets == []
        selected_seen = selected_stages
        return object()

    monkeypatch.setattr(orchestrator_module, "download_all_repos", fake_download)
    monkeypatch.setattr(orchestrator, "_run_assets", fake_run_assets)

    await orchestrator.resume(run_id)
    assert selected_seen == ("deps", "secrets")

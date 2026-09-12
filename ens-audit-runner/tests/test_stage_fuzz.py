"""Tests for bounded Foundry and Echidna fuzz-stage orchestration."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from ens_audit.models import Asset, Severity
from ens_audit.pipeline.stage_fuzz import FuzzStage


def _asset(tmp_path: Path, *, solidity: bool = True) -> Asset:
    """Build one local audit asset for fuzz-stage tests."""

    root = tmp_path / "asset"
    root.mkdir(exist_ok=True)
    return Asset("smart-account", root, "a" * 40, has_solidity=solidity)


@pytest.mark.asyncio
async def test_non_solidity_asset_skips_fuzzers(tmp_path: Path) -> None:
    """Assets without Solidity never invoke property fuzzers."""

    assert await FuzzStage().run(_asset(tmp_path, solidity=False)) == []


def test_parse_forge_handles_missing_empty_and_invalid_json(tmp_path: Path) -> None:
    """Missing or malformed Foundry JSON produces no fabricated finding."""

    asset = _asset(tmp_path)
    assert FuzzStage._parse_forge(tmp_path / "missing.json", asset) == []
    empty = tmp_path / "empty.json"
    empty.write_text("", encoding="utf-8")
    assert FuzzStage._parse_forge(empty, asset) == []
    invalid = tmp_path / "invalid.json"
    invalid.write_text("not-json", encoding="utf-8")
    assert FuzzStage._parse_forge(invalid, asset) == []


def test_parse_forge_normalizes_only_failed_records(tmp_path: Path) -> None:
    """Foundry success/non-mapping records are ignored while failures become high findings."""

    path = tmp_path / "forge.json"
    path.write_text(
        json.dumps(
            {
                "ok": {"status": "success", "name": "passes"},
                "bad": {"test_status": "FAILED", "test": "invariantBalance"},
                "noise": "ignored",
            }
        ),
        encoding="utf-8",
    )
    [finding] = FuzzStage._parse_forge(path, _asset(tmp_path))
    assert finding.title == "Foundry invariant failed: invariantBalance"
    assert finding.rule_id == "foundry-invariant"
    assert finding.severity is Severity.HIGH
    assert finding.root_cause == "property-violation"


def test_parse_forge_accepts_list_payload_and_default_name(tmp_path: Path) -> None:
    """List-form Foundry output and missing names use the documented fallback title."""

    path = tmp_path / "forge-list.json"
    path.write_text(json.dumps([{"status": "fail"}]), encoding="utf-8")
    [finding] = FuzzStage._parse_forge(path, _asset(tmp_path))
    assert finding.title == "Foundry invariant failed: Foundry invariant"


def test_tool_accepts_allowed_code_and_rejects_other_code(tmp_path: Path) -> None:
    """The fuzzer process boundary accepts only explicitly configured result codes."""

    stage = FuzzStage()

    class Runner:
        def __init__(self, code: int) -> None:
            self.code = code

        def run(self, *_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(["forge"], self.code, "stdout", "stderr")

    stage.tool_runner = Runner(0)  # type: ignore[assignment]
    completed = stage._tool(
        ["forge", "test"],
        cwd=tmp_path,
        timeout_s=1,
        accepted_codes={0, 1},
    )
    assert completed.returncode == 0

    stage.tool_runner = Runner(2)  # type: ignore[assignment]
    with pytest.raises(RuntimeError, match="forge failed: stderr"):
        stage._tool(["forge"], cwd=tmp_path, timeout_s=1, accepted_codes={0, 1})


def test_run_sync_normalizes_forge_and_echidna_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Available Solidity fuzzers produce normalized invariant/property findings."""

    monkeypatch.setattr("ens_audit.pipeline.stage_fuzz.RESULTS_DIR", tmp_path / "results")
    stage = FuzzStage()

    class Available:
        def available(self, _tool: str) -> bool:
            return True

    stage.tool_runner = Available()  # type: ignore[assignment]

    def fake_tool(
        argv: list[str],
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        if argv[0] == "forge":
            payload = json.dumps({"case": {"status": "failure", "name": "invariantOwner"}})
            return subprocess.CompletedProcess(argv, 1, payload, "")
        return subprocess.CompletedProcess(argv, 1, "property failed", "shrunk trace")

    monkeypatch.setattr(stage, "_tool", fake_tool)
    findings = stage._run_sync(_asset(tmp_path))

    assert {finding.rule_id for finding in findings} == {
        "foundry-invariant",
        "echidna-property-violation",
    }
    config = tmp_path / "results/smart-account/fuzz/echidna-config.yaml"
    assert "testLimit: 50000" in config.read_text(encoding="utf-8")
    echidna_output = tmp_path / "results/smart-account/fuzz/echidna.txt"
    assert "property failedshrunk trace" == echidna_output.read_text(encoding="utf-8")

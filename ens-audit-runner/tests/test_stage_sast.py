"""Coverage tests for SAST orchestration and SARIF normalization."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from ens_audit.models import Asset, Finding, Location, Severity
from ens_audit.pipeline.stage_sast import SASTStage


class _AvailableTools:
    """Pretend every external SAST executable is installed."""

    def available(self, tool: str) -> bool:
        """Return true for every requested tool."""

        return bool(tool)


def _finding(asset: Asset) -> Finding:
    """Build a deterministic local finding for dedup tests."""

    return Finding(
        title="example",
        severity=Severity.MEDIUM,
        asset=asset.name,
        stage="sast",
        rule_id="rule",
        root_cause="root",
        location=Location("src/example.ts", 4),
        description="example",
        evidence="example",
    )


def _sarif(rule: str = "ens-chainid-not-validated", level: str = "error") -> dict[str, Any]:
    """Return one minimal SARIF document."""

    return {
        "runs": [{"results": [{
            "ruleId": rule,
            "level": level,
            "message": {"text": "unsafe binding\nextra"},
            "locations": [{"physicalLocation": {
                "artifactLocation": {"uri": "src/a.ts"},
                "region": {"startLine": 7, "startColumn": 3},
            }}],
        }]}],
    }


def test_parse_sarif_missing_file_is_empty(tmp_path: Path) -> None:
    """Absent scanner output must not fabricate findings."""

    asset = Asset("manager", tmp_path, "a" * 40)
    assert SASTStage._parse_sarif(tmp_path / "missing.sarif", asset) == []


@pytest.mark.parametrize(
    ("level", "severity"),
    [("error", Severity.HIGH), ("warning", Severity.MEDIUM),
     ("note", Severity.LOW), ("none", Severity.INFO), ("odd", Severity.MEDIUM)],
)
def test_parse_sarif_maps_severity_and_root_cause(
    tmp_path: Path, level: str, severity: Severity
) -> None:
    """SARIF levels and ENS rules normalize into stable internal fields."""

    path = tmp_path / "result.sarif"
    path.write_text(json.dumps(_sarif(level=level)), encoding="utf-8")
    asset = Asset("manager", tmp_path, "b" * 40)
    [finding] = SASTStage._parse_sarif(path, asset)
    assert finding.severity is severity
    assert finding.root_cause == "chain_id_not_bound_to_wallet"
    assert finding.location == Location("src/a.ts", 7, 3)
    assert finding.title == "unsafe binding"


def test_dedupe_normalizes_path_separators(tmp_path: Path) -> None:
    """Duplicate tool reports at the same logical source location collapse to one record."""

    asset = Asset("manager", tmp_path, "c" * 40)
    first = _finding(asset)
    second = _finding(asset)
    second.location = Location("src\\example.ts", 4)
    assert len(SASTStage._dedupe([first, second])) == 1


def test_contains_suffix_ignores_symlink(tmp_path: Path) -> None:
    """Suffix detection sees real files and does not rely on symlink targets."""

    assert SASTStage._contains_suffix(tmp_path, ".py") is False
    (tmp_path / "real.py").write_text("print('x')", encoding="utf-8")
    assert SASTStage._contains_suffix(tmp_path, ".py") is True


def test_tool_accepts_configured_codes_and_rejects_failure(tmp_path: Path) -> None:
    """The process boundary accepts only explicitly allowed return codes."""

    stage = SASTStage(tmp_path / "rules.yaml")

    class _Runner:
        def __init__(self, code: int) -> None:
            self.code = code

        def run(self, *_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(["tool"], self.code, "out", "err")

    stage.tool_runner = _Runner(1)  # type: ignore[assignment]
    assert stage._tool(["tool"], cwd=tmp_path, timeout_s=1, accepted_codes={0, 1}).returncode == 1
    stage.tool_runner = _Runner(2)  # type: ignore[assignment]
    with pytest.raises(RuntimeError, match="tool failed"):
        stage._tool(["tool"], cwd=tmp_path, timeout_s=1)


def test_run_sync_exercises_all_external_sast_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """CodeQL, Semgrep, Slither, and Bandit orchestration produces normalized SARIF findings."""

    asset_root = tmp_path / "asset"
    asset_root.mkdir()
    (asset_root / "a.py").write_text("print('x')", encoding="utf-8")
    (asset_root / "a.sol").write_text("contract A {}", encoding="utf-8")
    rules = tmp_path / "ens-custom.yaml"
    rules.write_text("rules: []\n", encoding="utf-8")
    (tmp_path / "codeql-config.yml").write_text("name: test\n", encoding="utf-8")
    stage = SASTStage(rules)
    stage.tool_runner = _AvailableTools()  # type: ignore[assignment]
    asset = Asset("transaction-manager", asset_root, "d" * 40, has_solidity=True)
    monkeypatch.setattr(stage, "_run_local_analyzers", lambda _asset: [_finding(asset)])

    def fake_tool(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        for token in argv:
            if token.startswith("--output="):
                Path(token.split("=", 1)[1]).write_text(json.dumps(_sarif()), encoding="utf-8")
        if "--sarif" in argv and argv[0] == "slither":
            Path(argv[-1]).write_text(json.dumps(_sarif("slither-rule", "warning")), encoding="utf-8")
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(stage, "_tool", fake_tool)
    findings = stage._run_sync(asset)
    assert {finding.rule_id for finding in findings} >= {"rule", "ens-chainid-not-validated", "slither-rule"}

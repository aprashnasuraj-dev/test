"""Tests for bounded Mythril and Halmos symbolic-stage orchestration."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from ens_audit.models import Asset, Severity
from ens_audit.pipeline.stage_symbolic import SymbolicStage


def _asset(tmp_path: Path, *, solidity: bool = True) -> Asset:
    """Build one local audit asset for symbolic-stage tests."""

    root = tmp_path / "asset"
    root.mkdir(exist_ok=True)
    return Asset("smart-account", root, "a" * 40, has_solidity=solidity)


@pytest.mark.asyncio
async def test_non_solidity_asset_skips_symbolic_tools(tmp_path: Path) -> None:
    """Assets without Solidity never invoke symbolic analyzers."""

    assert await SymbolicStage().run(_asset(tmp_path, solidity=False)) == []


def test_parse_mythril_handles_missing_empty_and_normalized_issue(tmp_path: Path) -> None:
    """Missing output is harmless and Mythril issues normalize into stable findings."""

    asset = _asset(tmp_path)
    assert SymbolicStage._parse_mythril(tmp_path / "missing.json", asset) == []
    empty = tmp_path / "empty.json"
    empty.write_text("", encoding="utf-8")
    assert SymbolicStage._parse_mythril(empty, asset) == []

    path = tmp_path / "mythril.json"
    path.write_text(
        json.dumps(
            {
                "issues": [
                    {
                        "title": "Unsafe delegatecall",
                        "severity": "High",
                        "swc-id": "SWC-112",
                        "filename": "Risky.sol",
                        "lineno": 9,
                        "description": "delegatecall target is user controlled",
                        "debug": "trace",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    [finding] = SymbolicStage._parse_mythril(path, asset)
    assert finding.rule_id == "SWC-112"
    assert finding.root_cause == "SWC-112"
    assert finding.severity is Severity.HIGH
    assert finding.location.file == "Risky.sol"
    assert finding.location.line == 9


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Critical", Severity.CRITICAL),
        ("high", Severity.HIGH),
        (" medium ", Severity.MEDIUM),
        ("low", Severity.LOW),
        ("info", Severity.INFO),
        ("unexpected", Severity.MEDIUM),
    ],
)
def test_mythril_severity_mapping(value: str, expected: Severity) -> None:
    """Symbolic severity text maps into the closed internal severity enum."""

    assert SymbolicStage._severity(value) is expected


def test_parse_halmos_handles_missing_zero_and_counterexample_records(tmp_path: Path) -> None:
    """Halmos emits findings only for explicit positive counterexample counts."""

    asset = _asset(tmp_path)
    assert SymbolicStage._parse_halmos(tmp_path / "missing.json", asset) == []
    empty = tmp_path / "empty.json"
    empty.write_text("", encoding="utf-8")
    assert SymbolicStage._parse_halmos(empty, asset) == []

    path = tmp_path / "halmos.json"
    path.write_text(
        json.dumps(
            {
                "results": [
                    "ignored",
                    {"name": "clean", "num_cexes": 0},
                    {
                        "function": "checkOwner",
                        "counterexamples": 2,
                        "file": "Invariant.t.sol",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    [finding] = SymbolicStage._parse_halmos(path, asset)
    assert finding.rule_id == "halmos-counterexample"
    assert finding.severity is Severity.HIGH
    assert finding.title == "Halmos counterexample: checkOwner"
    assert "2 counterexample(s)" in finding.description


def test_parse_halmos_accepts_list_payload(tmp_path: Path) -> None:
    """List-form Halmos output is normalized directly."""

    path = tmp_path / "halmos-list.json"
    path.write_text(json.dumps([{"name": "invariantX", "num_cexes": 1}]), encoding="utf-8")
    [finding] = SymbolicStage._parse_halmos(path, _asset(tmp_path))
    assert finding.title == "Halmos counterexample: invariantX"


def test_tool_accepts_allowed_code_and_rejects_other_code(tmp_path: Path) -> None:
    """Symbolic subprocesses fail closed outside their accepted result codes."""

    stage = SymbolicStage()

    class Runner:
        def __init__(self, code: int) -> None:
            self.code = code

        def run(self, *_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(["myth"], self.code, "stdout", "stderr")

    stage.tool_runner = Runner(1)  # type: ignore[assignment]
    assert stage._tool(
        ["myth", "analyze"],
        cwd=tmp_path,
        timeout_s=1,
        accepted_codes={0, 1},
    ).returncode == 1

    stage.tool_runner = Runner(3)  # type: ignore[assignment]
    with pytest.raises(RuntimeError, match="myth failed: stderr"):
        stage._tool(["myth"], cwd=tmp_path, timeout_s=1, accepted_codes={0, 1})


def test_run_sync_normalizes_mythril_and_halmos_results(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Available symbolic analyzers both contribute normalized findings."""

    monkeypatch.setattr("ens_audit.pipeline.stage_symbolic.RESULTS_DIR", tmp_path / "results")
    stage = SymbolicStage()

    class Available:
        def available(self, _tool: str) -> bool:
            return True

    stage.tool_runner = Available()  # type: ignore[assignment]

    def fake_tool(
        argv: list[str],
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        if argv[0] == "myth":
            payload = json.dumps(
                {
                    "issues": [
                        {
                            "title": "Myth issue",
                            "severity": "Medium",
                            "swcID": "SWC-999",
                        }
                    ]
                }
            )
            return subprocess.CompletedProcess(argv, 0, payload, "")
        output = Path(argv[argv.index("--json-output") + 1])
        output.write_text(
            json.dumps({"results": [{"name": "halmosInvariant", "num_cexes": 1}]}),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(stage, "_tool", fake_tool)
    findings = stage._run_sync(_asset(tmp_path))
    assert {finding.rule_id for finding in findings} == {"SWC-999", "halmos-counterexample"}

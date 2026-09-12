"""Tests for dependency vulnerability scanner orchestration."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from ens_audit.models import Asset, Severity
from ens_audit.pipeline import stage_deps as deps_module
from ens_audit.pipeline.stage_deps import DependencyStage


def _asset(tmp_path: Path) -> Asset:
    """Build an asset containing all supported package manifests."""

    root = tmp_path / "asset"
    root.mkdir(exist_ok=True)
    (root / "package.json").write_text("{}", encoding="utf-8")
    (root / "package-lock.json").write_text("{}", encoding="utf-8")
    (root / "requirements.txt").write_text("demo==1.0\n", encoding="utf-8")
    return Asset("manager", root, "a" * 40)


def test_json_handles_absent_and_empty_files(tmp_path: Path) -> None:
    """Missing or blank scanner files normalize to an empty object."""

    assert DependencyStage._json(tmp_path / "missing.json") == {}
    empty = tmp_path / "empty.json"
    empty.write_text("", encoding="utf-8")
    assert DependencyStage._json(empty) == {}


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("critical", Severity.CRITICAL),
        ("high", Severity.HIGH),
        ("moderate", Severity.MEDIUM),
        ("medium", Severity.MEDIUM),
        ("low", Severity.LOW),
        ("info", Severity.INFO),
        ("unknown", Severity.MEDIUM),
    ],
)
def test_severity_mapping(text: str, expected: Severity) -> None:
    """Dependency scanner severities map into the closed internal enum."""

    assert DependencyStage._severity(text) is expected


def test_parsers_ignore_non_mapping_records(tmp_path: Path) -> None:
    """Malformed list entries are skipped while valid vulnerabilities remain reportable."""

    asset = _asset(tmp_path)
    npm = tmp_path / "npm.json"
    npm.write_text(
        json.dumps({"vulnerabilities": {"bad": "skip", "pkg": {"severity": "high", "via": ["CVE"]}}}),
        encoding="utf-8",
    )
    snyk = tmp_path / "snyk.json"
    snyk.write_text(
        json.dumps({"vulnerabilities": ["skip", {"id": "SNYK-1", "title": "issue", "severity": "low"}]}),
        encoding="utf-8",
    )
    pip = tmp_path / "pip.json"
    pip.write_text(
        json.dumps({"dependencies": ["skip", {"name": "demo", "vulns": ["skip", {"id": "PYSEC-1"}]}]}),
        encoding="utf-8",
    )
    assert DependencyStage._parse_npm(npm, asset)[0].severity is Severity.HIGH
    assert DependencyStage._parse_snyk(snyk, asset)[0].rule_id == "SNYK-1"
    assert DependencyStage._parse_pip(pip, asset)[0].rule_id == "PYSEC-1"


def test_tool_rejects_unaccepted_exit(tmp_path: Path) -> None:
    """Scanner failures outside the documented result codes fail closed."""

    stage = DependencyStage()

    class _Runner:
        def run(self, *_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(["scanner"], 9, "", "dependency scanner failed")

    stage.tool_runner = _Runner()  # type: ignore[assignment]
    with pytest.raises(RuntimeError, match="dependency scanner failed"):
        stage._tool(["scanner"], cwd=tmp_path, timeout_s=1, accepted_codes={0, 1})


@pytest.mark.asyncio
async def test_run_executes_npm_snyk_and_pip_audit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """All applicable scanners run and their machine-readable findings are normalized."""

    monkeypatch.setattr(deps_module, "RESULTS_DIR", tmp_path / "results")

    class _Runner:
        def available(self, _tool: str) -> bool:
            return True

        def run(
            self, tool: str, _args: object, **_kwargs: object
        ) -> subprocess.CompletedProcess[str]:
            payloads = {
                "npm": {"vulnerabilities": {"leftpad": {"severity": "critical", "via": ["CVE-1"]}}},
                "snyk": {"vulnerabilities": [{"id": "SNYK-2", "title": "snyk issue", "severity": "high"}]},
                "pip-audit": {"dependencies": [{"name": "demo", "vulns": [{"id": "PYSEC-2"}]}]},
            }
            return subprocess.CompletedProcess([tool], 1, json.dumps(payloads[tool]), "")

    stage = DependencyStage()
    stage.tool_runner = _Runner()  # type: ignore[assignment]
    findings = await stage.run(_asset(tmp_path))
    assert {finding.rule_id for finding in findings} == {"npm:leftpad", "SNYK-2", "PYSEC-2"}
    assert all(finding.root_cause == "vulnerable-dependency" for finding in findings)

"""Stage 2: bounded symbolic analysis for Solidity-bearing assets."""

from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any

from ens_audit.config import RESULTS_DIR
from ens_audit.models import Asset, Finding, Location, Severity
from ens_audit.tooling import DEFAULT_TOOL_RUNNER


class SymbolicStage:
    """Run bounded Mythril and Halmos analysis for Solidity assets.

    Security invariant: symbolic tools run only against the checked-out asset path with
    fixed bounds and without shell interpretation.
    """

    def __init__(self) -> None:
        self.tool_runner = DEFAULT_TOOL_RUNNER

    async def run(self, asset: Asset) -> list[Finding]:
        """Run symbolic analyzers when Solidity is present and normalize supported output."""

        if not asset.has_solidity:
            return []
        return await asyncio.to_thread(self._run_sync, asset)

    def _run_sync(self, asset: Asset) -> list[Finding]:
        """Execute bounded symbolic tools for one asset."""

        output_dir = RESULTS_DIR / asset.name / "symbolic"
        output_dir.mkdir(parents=True, exist_ok=True)
        findings: list[Finding] = []

        if self.tool_runner.available("myth"):
            mythril_path = output_dir / "mythril.json"
            completed = self._tool(
                [
                    "myth",
                    "analyze",
                    str(asset.path),
                    "--execution-timeout",
                    "300",
                    "--max-depth",
                    "128",
                    "--solver-timeout",
                    "30000",
                    "--transaction-count",
                    "2",
                    "-o",
                    "json",
                ],
                cwd=asset.path,
                timeout_s=360,
                accepted_codes={0, 1},
            )
            mythril_path.write_text(completed.stdout, encoding="utf-8")
            findings.extend(self._parse_mythril(mythril_path, asset))

        if self.tool_runner.available("halmos"):
            halmos_path = output_dir / "halmos.json"
            self._tool(
                [
                    "halmos",
                    "--loop",
                    "10",
                    "--solver-timeout-assertion",
                    "30000",
                    "--json-output",
                    str(halmos_path),
                ],
                cwd=asset.path,
                timeout_s=360,
                accepted_codes={0, 1},
            )
            findings.extend(self._parse_halmos(halmos_path, asset))

        return findings

    def _tool(
        self,
        argv: list[str],
        *,
        cwd: Path,
        timeout_s: int,
        accepted_codes: set[int],
    ) -> subprocess.CompletedProcess[str]:
        """Run a symbolic tool natively or through WSL as an argv-only child process."""

        completed = self.tool_runner.run(
            argv[0],
            argv[1:],
            cwd=cwd,
            timeout_s=timeout_s,
        )
        if completed.returncode not in accepted_codes:
            detail = completed.stderr.strip() or completed.stdout.strip() or "tool failed"
            raise RuntimeError(f"{argv[0]} failed: {detail[:2000]}")
        return completed

    @staticmethod
    def _parse_mythril(path: Path, asset: Asset) -> list[Finding]:
        """Normalize Mythril's JSON ``issues`` array."""

        if not path.exists() or not path.read_text(encoding="utf-8").strip():
            return []
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        findings: list[Finding] = []
        for issue in data.get("issues", []):
            title = str(issue.get("title", "Mythril symbolic finding"))
            severity = SymbolicStage._severity(str(issue.get("severity", "Medium")))
            findings.append(
                Finding(
                    title=title,
                    severity=severity,
                    asset=asset.name,
                    stage="symbolic",
                    rule_id=str(issue.get("swc-id", issue.get("swcID", "mythril"))),
                    root_cause=str(issue.get("swc-id", issue.get("swcID", "mythril"))),
                    location=Location(
                        file=str(issue.get("filename", "")),
                        line=int(issue.get("lineno", 0) or 0),
                    ),
                    description=str(issue.get("description", title)),
                    evidence=str(issue.get("debug", issue.get("description", title))),
                    confidence=0.9,
                )
            )
        return findings

    @staticmethod
    def _parse_halmos(path: Path, asset: Asset) -> list[Finding]:
        """Normalize only explicit Halmos counterexample records present in JSON output."""

        if not path.exists() or not path.read_text(encoding="utf-8").strip():
            return []
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
        records = payload if isinstance(payload, list) else payload.get("results", [])
        findings: list[Finding] = []
        for record in records:
            if not isinstance(record, dict):
                continue
            count = int(record.get("num_cexes", record.get("counterexamples", 0)) or 0)
            if count <= 0:
                continue
            name = str(record.get("name", record.get("function", "Halmos counterexample")))
            findings.append(
                Finding(
                    title=f"Halmos counterexample: {name}",
                    severity=Severity.HIGH,
                    asset=asset.name,
                    stage="symbolic",
                    rule_id="halmos-counterexample",
                    root_cause="symbolic-counterexample",
                    location=Location(file=str(record.get("file", ""))),
                    description=f"Halmos reported {count} counterexample(s) for {name}.",
                    evidence=json.dumps(record, sort_keys=True)[:12000],
                    confidence=0.9,
                )
            )
        return findings

    @staticmethod
    def _severity(value: str) -> Severity:
        """Map analyzer severity text into the closed internal severity enum."""

        normalized = value.strip().lower()
        return {
            "critical": Severity.CRITICAL,
            "high": Severity.HIGH,
            "medium": Severity.MEDIUM,
            "low": Severity.LOW,
            "info": Severity.INFO,
        }.get(normalized, Severity.MEDIUM)

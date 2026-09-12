"""Stage 1: static application security testing across the scoped ENS assets."""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from ens_audit.config import RESULTS_DIR
from ens_audit.models import Asset, Finding, Location, Severity


class SASTStage:
    """Run CodeQL, Semgrep, Slither, and Bandit and normalize their findings.

    Security invariant: external tools receive only argv lists and fixed output paths; shell
    interpretation is never enabled.
    """

    def __init__(self, custom_rules: Path) -> None:
        self.custom_rules = custom_rules

    async def run(self, asset: Asset) -> list[Finding]:
        """Run all applicable SAST tools for one asset and return normalized findings."""

        return await asyncio.to_thread(self._run_sync, asset)

    def _run_sync(self, asset: Asset) -> list[Finding]:
        """Execute the synchronous SAST workflow for one asset."""

        output_dir = RESULTS_DIR / asset.name / "sast"
        output_dir.mkdir(parents=True, exist_ok=True)
        sarif_files: list[Path] = []

        if shutil.which("codeql"):
            database = output_dir / "codeql-db"
            self._tool(
                [
                    "codeql",
                    "database",
                    "create",
                    str(database),
                    "--language=javascript",
                    f"--source-root={asset.path}",
                ],
                cwd=asset.path,
                timeout_s=1800,
            )
            codeql_sarif = output_dir / "codeql.sarif"
            self._tool(
                [
                    "codeql",
                    "database",
                    "analyze",
                    str(database),
                    "javascript-security-extended.qls",
                    "--format=sarif-latest",
                    f"--output={codeql_sarif}",
                ],
                cwd=asset.path,
                timeout_s=1800,
            )
            sarif_files.append(codeql_sarif)

        if shutil.which("semgrep"):
            semgrep_sarif = output_dir / "semgrep.sarif"
            self._tool(
                [
                    "semgrep",
                    "--config=p/typescript",
                    "--config=p/javascript",
                    f"--config={self.custom_rules}",
                    "--sarif",
                    f"--output={semgrep_sarif}",
                    str(asset.path),
                ],
                cwd=asset.path,
                timeout_s=1800,
            )
            sarif_files.append(semgrep_sarif)

        if asset.has_solidity and shutil.which("slither"):
            slither_sarif = output_dir / "slither.sarif"
            self._tool(
                ["slither", str(asset.path), "--sarif", str(slither_sarif)],
                cwd=asset.path,
                timeout_s=1800,
            )
            sarif_files.append(slither_sarif)

        if self._contains_suffix(asset.path, ".py") and shutil.which("bandit"):
            bandit_json = output_dir / "bandit.json"
            self._tool(
                ["bandit", "-r", str(asset.path), "-f", "json", "-o", str(bandit_json)],
                cwd=asset.path,
                timeout_s=1800,
                accepted_codes={0, 1},
            )

        findings: list[Finding] = []
        for sarif_path in sarif_files:
            findings.extend(self._parse_sarif(sarif_path, asset))
        return findings

    @staticmethod
    def _tool(
        argv: list[str],
        *,
        cwd: Path,
        timeout_s: int,
        accepted_codes: set[int] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """Execute one external analyzer without shell interpretation."""

        accepted = accepted_codes or {0}
        completed = subprocess.run(
            argv,
            cwd=cwd,
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        if completed.returncode not in accepted:
            message = completed.stderr.strip() or completed.stdout.strip() or "tool failed"
            raise RuntimeError(f"{argv[0]} failed: {message[:2000]}")
        return completed

    @staticmethod
    def _contains_suffix(root: Path, suffix: str) -> bool:
        """Return whether a source suffix exists without following symlink directories."""

        return any(path.is_file() for path in root.rglob(f"*{suffix}") if not path.is_symlink())

    @staticmethod
    def _parse_sarif(path: Path, asset: Asset) -> list[Finding]:
        """Normalize SARIF results into internal findings without executing embedded data."""

        if not path.exists():
            return []
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        findings: list[Finding] = []
        for run in data.get("runs", []):
            for result in run.get("results", []):
                rule_id = str(result.get("ruleId", "unknown"))
                message = str(result.get("message", {}).get("text", rule_id))
                physical = ((result.get("locations") or [{}])[0].get("physicalLocation") or {})
                artifact = str((physical.get("artifactLocation") or {}).get("uri", ""))
                region = physical.get("region") or {}
                level = str(result.get("level", "warning")).lower()
                severity = {
                    "error": Severity.HIGH,
                    "warning": Severity.MEDIUM,
                    "note": Severity.LOW,
                    "none": Severity.INFO,
                }.get(level, Severity.MEDIUM)
                findings.append(
                    Finding(
                        title=message.splitlines()[0][:200],
                        severity=severity,
                        asset=asset.name,
                        stage="sast",
                        rule_id=rule_id,
                        root_cause=rule_id,
                        location=Location(
                            file=artifact,
                            line=int(region.get("startLine", 0) or 0),
                            column=int(region.get("startColumn", 0) or 0),
                        ),
                        description=message,
                        evidence=message,
                    )
                )
        return findings

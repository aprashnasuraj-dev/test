"""Stage 4: dependency vulnerability auditing."""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from ens_audit.config import RESULTS_DIR
from ens_audit.models import Asset, Finding, Location, Severity


class DependencyStage:
    """Run npm/Snyk/pip dependency checks and normalize machine-readable findings.

    Security invariant: package managers and scanners execute as argv-only subprocesses in
    the pinned asset directory; their output is treated strictly as data.
    """

    async def run(self, asset: Asset) -> list[Finding]:
        """Run dependency scanners applicable to one asset."""

        return await asyncio.to_thread(self._run_sync, asset)

    def _run_sync(self, asset: Asset) -> list[Finding]:
        """Execute dependency audits and return normalized findings."""

        output_dir = RESULTS_DIR / asset.name / "deps"
        output_dir.mkdir(parents=True, exist_ok=True)
        findings: list[Finding] = []

        if (asset.path / "package.json").is_file() and shutil.which("npm"):
            completed = self._tool(
                ["npm", "audit", "--json"],
                cwd=asset.path,
                timeout_s=600,
                accepted_codes={0, 1},
            )
            npm_path = output_dir / "npm-audit.json"
            npm_path.write_text(completed.stdout, encoding="utf-8")
            findings.extend(self._parse_npm(npm_path, asset))

        if (asset.path / "package.json").is_file() and shutil.which("npx"):
            completed = self._tool(
                ["npx", "snyk", "test", "--json"],
                cwd=asset.path,
                timeout_s=600,
                accepted_codes={0, 1, 2, 3},
            )
            snyk_path = output_dir / "snyk.json"
            snyk_path.write_text(completed.stdout, encoding="utf-8")
            findings.extend(self._parse_snyk(snyk_path, asset))

        requirements = asset.path / "requirements.txt"
        if requirements.is_file() and shutil.which("pip-audit"):
            completed = self._tool(
                ["pip-audit", "-r", str(requirements), "--format=json"],
                cwd=asset.path,
                timeout_s=600,
                accepted_codes={0, 1},
            )
            pip_path = output_dir / "pip-audit.json"
            pip_path.write_text(completed.stdout, encoding="utf-8")
            findings.extend(self._parse_pip(pip_path, asset))

        return findings

    @staticmethod
    def _tool(
        argv: list[str],
        *,
        cwd: Path,
        timeout_s: int,
        accepted_codes: set[int],
    ) -> subprocess.CompletedProcess[str]:
        """Execute one dependency scanner without a shell."""

        completed = subprocess.run(
            argv,
            cwd=cwd,
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        if completed.returncode not in accepted_codes:
            detail = completed.stderr.strip() or completed.stdout.strip() or "tool failed"
            raise RuntimeError(f"{argv[0]} failed: {detail[:2000]}")
        return completed

    @staticmethod
    def _parse_npm(path: Path, asset: Asset) -> list[Finding]:
        """Normalize npm audit vulnerability objects."""

        payload = DependencyStage._json(path)
        vulnerabilities = payload.get("vulnerabilities", {}) if isinstance(payload, dict) else {}
        findings: list[Finding] = []
        for package, record in vulnerabilities.items():
            if not isinstance(record, dict):
                continue
            severity = DependencyStage._severity(str(record.get("severity", "medium")))
            via = record.get("via", [])
            findings.append(
                DependencyStage._finding(
                    asset,
                    f"npm dependency vulnerability: {package}",
                    severity,
                    f"npm:{package}",
                    json.dumps(via, sort_keys=True)[:12000],
                )
            )
        return findings

    @staticmethod
    def _parse_snyk(path: Path, asset: Asset) -> list[Finding]:
        """Normalize Snyk vulnerability records."""

        payload = DependencyStage._json(path)
        records = payload.get("vulnerabilities", []) if isinstance(payload, dict) else []
        return [
            DependencyStage._finding(
                asset,
                str(record.get("title", "Snyk dependency vulnerability")),
                DependencyStage._severity(str(record.get("severity", "medium"))),
                str(record.get("id", "snyk")),
                json.dumps(record, sort_keys=True)[:12000],
            )
            for record in records
            if isinstance(record, dict)
        ]

    @staticmethod
    def _parse_pip(path: Path, asset: Asset) -> list[Finding]:
        """Normalize pip-audit dependency records."""

        payload = DependencyStage._json(path)
        records = payload.get("dependencies", []) if isinstance(payload, dict) else []
        findings: list[Finding] = []
        for dependency in records:
            if not isinstance(dependency, dict):
                continue
            for vulnerability in dependency.get("vulns", []):
                if isinstance(vulnerability, dict):
                    findings.append(
                        DependencyStage._finding(
                            asset,
                            f"Python dependency vulnerability: {dependency.get('name', 'unknown')}",
                            Severity.MEDIUM,
                            str(vulnerability.get("id", "pip-audit")),
                            json.dumps(vulnerability, sort_keys=True)[:12000],
                        )
                    )
        return findings

    @staticmethod
    def _json(path: Path) -> Any:
        """Load JSON scanner output, returning an empty object for absent/empty output."""

        if not path.exists() or not path.read_text(encoding="utf-8").strip():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _severity(value: str) -> Severity:
        """Map dependency-scanner severity text to the internal enum."""

        return {
            "critical": Severity.CRITICAL,
            "high": Severity.HIGH,
            "moderate": Severity.MEDIUM,
            "medium": Severity.MEDIUM,
            "low": Severity.LOW,
            "info": Severity.INFO,
        }.get(value.lower(), Severity.MEDIUM)

    @staticmethod
    def _finding(asset: Asset, title: str, severity: Severity, rule_id: str, evidence: str) -> Finding:
        """Build one normalized dependency finding."""

        return Finding(
            title=title,
            severity=severity,
            asset=asset.name,
            stage="deps",
            rule_id=rule_id,
            root_cause="vulnerable-dependency",
            location=Location(file="package manifest"),
            description=title,
            evidence=evidence,
        )

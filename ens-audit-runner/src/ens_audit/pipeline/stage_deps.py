"""Stage 4: dependency vulnerability auditing."""

from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any

from ens_audit.config import RESULTS_DIR
from ens_audit.models import Asset, Finding, Location, Severity
from ens_audit.tooling import DEFAULT_TOOL_RUNNER


class DependencyStage:
    """Run npm/Snyk/pip dependency checks and normalize machine-readable findings.

    Security invariant: package managers and scanners execute as argv-only subprocesses in
    the pinned asset directory; no scanner is implicitly downloaded through ``npx``.
    """

    _EXCLUDED_DIRS = {".git", ".venv", "venv", "node_modules"}

    def __init__(self) -> None:
        self.tool_runner = DEFAULT_TOOL_RUNNER

    async def run(self, asset: Asset) -> list[Finding]:
        """Run dependency scanners applicable to one asset."""

        return await asyncio.to_thread(self._run_sync, asset)

    def _run_sync(self, asset: Asset) -> list[Finding]:
        """Execute dependency audits and return normalized findings."""

        output_dir = RESULTS_DIR / asset.name / "deps"
        output_dir.mkdir(parents=True, exist_ok=True)
        findings: list[Finding] = []

        if self.tool_runner.available("npm"):
            for index, package_root in enumerate(self._npm_project_roots(asset.path)):
                completed = self._tool(
                    ["npm", "audit", "--json"],
                    cwd=package_root,
                    timeout_s=2400,
                    accepted_codes={0, 1},
                )
                npm_path = output_dir / f"npm-audit-{index:03d}.json"
                npm_path.write_text(completed.stdout, encoding="utf-8")
                findings.extend(self._parse_npm(npm_path, asset))

        if self.tool_runner.available("snyk") and self._contains_package_manifest(asset.path):
            completed = self._tool(
                ["snyk", "test", "--all-projects", "--json"],
                cwd=asset.path,
                timeout_s=2400,
                accepted_codes={0, 1, 2, 3},
            )
            snyk_path = output_dir / "snyk.json"
            snyk_path.write_text(completed.stdout, encoding="utf-8")
            findings.extend(self._parse_snyk(snyk_path, asset))

        requirements = self._requirement_files(asset.path)
        if requirements and self.tool_runner.available("pip-audit"):
            args = ["pip-audit"]
            for requirement in requirements:
                args.extend(["-r", str(requirement)])
            args.append("--format=json")
            completed = self._tool(
                args,
                cwd=asset.path,
                timeout_s=2400,
                accepted_codes={0, 1},
            )
            pip_path = output_dir / "pip-audit.json"
            pip_path.write_text(completed.stdout, encoding="utf-8")
            findings.extend(self._parse_pip(pip_path, asset))

        return findings

    @classmethod
    def _npm_project_roots(cls, root: Path) -> list[Path]:
        """Return package roots that have an npm lockfile, including nested projects."""

        roots: set[Path] = set()
        for lock_name in ("package-lock.json", "npm-shrinkwrap.json"):
            for lock in root.rglob(lock_name):
                if lock.is_symlink() or cls._excluded(root, lock):
                    continue
                package_json = lock.parent / "package.json"
                if package_json.is_file() and not package_json.is_symlink():
                    roots.add(lock.parent.resolve())
        return sorted(roots, key=lambda path: path.as_posix())

    @classmethod
    def _requirement_files(cls, root: Path) -> list[Path]:
        """Return all in-scope requirements text files for one asset."""

        files = {
            path.resolve()
            for path in root.rglob("requirements*.txt")
            if path.is_file() and not path.is_symlink() and not cls._excluded(root, path)
        }
        return sorted(files, key=lambda path: path.as_posix())

    @classmethod
    def _contains_package_manifest(cls, root: Path) -> bool:
        """Return whether an in-scope JavaScript package manifest exists."""

        return any(
            path.is_file() and not path.is_symlink() and not cls._excluded(root, path)
            for path in root.rglob("package.json")
        )

    @classmethod
    def _excluded(cls, root: Path, path: Path) -> bool:
        """Exclude dependency caches, virtual environments, and VCS internals."""

        try:
            relative = path.relative_to(root)
        except ValueError:
            return True
        return any(part in cls._EXCLUDED_DIRS for part in relative.parts)

    def _tool(
        self,
        argv: list[str],
        *,
        cwd: Path,
        timeout_s: int,
        accepted_codes: set[int],
    ) -> subprocess.CompletedProcess[str]:
        """Execute one dependency scanner natively or through WSL without a shell."""

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
        """Normalize Snyk vulnerability records from single or multi-project output."""

        payload = DependencyStage._json(path)
        projects = payload if isinstance(payload, list) else [payload]
        findings: list[Finding] = []
        for project in projects:
            if not isinstance(project, dict):
                continue
            records = project.get("vulnerabilities", [])
            if not isinstance(records, list):
                continue
            findings.extend(
                DependencyStage._finding(
                    asset,
                    str(record.get("title", "Snyk dependency vulnerability")),
                    DependencyStage._severity(str(record.get("severity", "medium"))),
                    str(record.get("id", "snyk")),
                    json.dumps(record, sort_keys=True)[:12000],
                )
                for record in records
                if isinstance(record, dict)
            )
        return findings

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

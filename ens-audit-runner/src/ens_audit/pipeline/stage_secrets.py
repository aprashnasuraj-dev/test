"""Stage 5: secret scanning with secret-value suppression."""

from __future__ import annotations

import asyncio
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from ens_audit.config import RESULTS_DIR
from ens_audit.models import Asset, Finding, Location, Severity
from ens_audit.tooling import DEFAULT_TOOL_RUNNER


class SecretStage:
    """Run TruffleHog and detect-secrets without retaining discovered secret values.

    Security invariant: raw scanner output is parsed only in memory; persisted artifacts,
    normalized findings, logs, evidence, and reports never contain matched secret material.
    """

    def __init__(self) -> None:
        self.tool_runner = DEFAULT_TOOL_RUNNER

    async def run(self, asset: Asset) -> list[Finding]:
        """Scan one asset for committed or present secret material."""

        return await asyncio.to_thread(self._run_sync, asset)

    def _run_sync(self, asset: Asset) -> list[Finding]:
        """Execute available secret scanners and persist metadata-only results."""

        output_dir = RESULTS_DIR / asset.name / "secrets"
        output_dir.mkdir(parents=True, exist_ok=True)
        findings: list[Finding] = []
        sanitized: list[dict[str, Any]] = []

        if self.tool_runner.available("trufflehog"):
            argv, cwd, include_file = self._trufflehog_command(asset, output_dir)
            scans: list[tuple[list[str], Path]] = [(argv, cwd)]
            if len(argv) > 1 and argv[1] == "git":
                scans.append(
                    (["trufflehog", "filesystem", str(asset.path), "--json"], asset.path)
                )
            try:
                for scan_argv, scan_cwd in scans:
                    completed = self._tool(scan_argv, cwd=scan_cwd, timeout_s=3600)
                    scanner_findings, scanner_metadata = self._parse_trufflehog_text(
                        completed.stdout,
                        asset,
                    )
                    findings.extend(scanner_findings)
                    sanitized.extend(scanner_metadata)
            finally:
                if include_file is not None:
                    include_file.unlink(missing_ok=True)

        if self.tool_runner.available("detect-secrets"):
            completed = self._tool(
                ["detect-secrets", "scan", str(asset.path), "--all-files"],
                cwd=asset.path,
                timeout_s=3600,
            )
            scanner_findings, scanner_metadata = self._parse_detect_secrets_text(
                completed.stdout,
                asset,
            )
            findings.extend(scanner_findings)
            sanitized.extend(scanner_metadata)

        findings = self._dedupe_findings(findings)
        sanitized = self._dedupe_metadata(sanitized)
        (output_dir / "secret-findings-sanitized.json").write_text(
            json.dumps(sanitized, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return findings

    @staticmethod
    def _trufflehog_command(
        asset: Asset,
        output_dir: Path,
    ) -> tuple[list[str], Path, Path | None]:
        """Build a history-aware, scope-restricted TruffleHog command.

        The audit assets are subdirectories of one monorepo, not independent Git
        repositories. TruffleHog's git source must therefore receive the true repository
        root. An ephemeral include-path file restricts history scanning to the current
        asset. A non-Git checkout falls back to filesystem scanning rather than producing a
        false scanner failure.
        """

        root_lookup = subprocess.run(
            ["git", "-C", str(asset.path), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if root_lookup.returncode != 0:
            return ["trufflehog", "filesystem", str(asset.path), "--json"], asset.path, None

        repo_root = Path(root_lookup.stdout.strip()).resolve()
        try:
            scope = asset.path.resolve().relative_to(repo_root).as_posix()
        except ValueError as exc:
            raise RuntimeError(
                f"asset path is outside its Git repository root: {asset.path}"
            ) from exc

        include_file = output_dir / ".trufflehog-include-paths"
        scope_pattern = rf"^{re.escape(scope)}(?:/.*)?$"
        include_file.write_text(scope_pattern + "\n", encoding="utf-8")
        return (
            [
                "trufflehog",
                "git",
                repo_root.as_uri(),
                "--json",
                "--include-paths",
                str(include_file),
            ],
            repo_root,
            include_file,
        )

    def _tool(
        self,
        argv: list[str],
        *,
        cwd: Path,
        timeout_s: int,
    ) -> subprocess.CompletedProcess[str]:
        """Run a secret scanner natively or through WSL without shell interpretation."""

        completed = self.tool_runner.run(
            argv[0],
            argv[1:],
            cwd=cwd,
            timeout_s=timeout_s,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or "secret scanner failed"
            raise RuntimeError(f"{argv[0]} failed: {detail[:2000]}")
        return completed

    @staticmethod
    def _parse_trufflehog_text(
        text: str,
        asset: Asset,
    ) -> tuple[list[Finding], list[dict[str, Any]]]:
        """Normalize TruffleHog JSON-lines text while discarding all secret-bearing fields."""

        findings: list[Finding] = []
        metadata: list[dict[str, Any]] = []
        for line in text.splitlines():
            if not line.strip():
                continue
            record: dict[str, Any] = json.loads(line)
            detector = str(record.get("DetectorName", "secret"))
            verified = bool(record.get("Verified", False))
            source = record.get("SourceMetadata") or {}
            data = source.get("Data") if isinstance(source, dict) else {}
            git_data = data.get("Git") if isinstance(data, dict) else {}
            filesystem_data = data.get("Filesystem") if isinstance(data, dict) else {}
            source_data: dict[str, Any]
            if isinstance(git_data, dict) and git_data:
                source_data = git_data
            elif isinstance(filesystem_data, dict):
                source_data = filesystem_data
            else:
                source_data = {}
            file_name = str(source_data.get("file", ""))
            line_number = int(source_data.get("line", 0) or 0)
            metadata.append(
                {
                    "scanner": "trufflehog",
                    "detector": detector,
                    "verified": verified,
                    "file": file_name,
                    "line": line_number,
                }
            )
            findings.append(
                Finding(
                    title=f"Potential secret detected: {detector}",
                    severity=Severity.HIGH if verified else Severity.MEDIUM,
                    asset=asset.name,
                    stage="secrets",
                    rule_id=f"trufflehog:{detector}",
                    root_cause="committed_credentials",
                    location=Location(file=file_name, line=line_number),
                    description="Secret scanner identified credential-like material.",
                    evidence=f"detector={detector}; verified={verified}",
                    confidence=1.0 if verified else 0.7,
                )
            )
        return findings, metadata

    @staticmethod
    def _parse_detect_secrets_text(
        text: str,
        asset: Asset,
    ) -> tuple[list[Finding], list[dict[str, Any]]]:
        """Normalize detect-secrets JSON text without retaining matched or hashed values."""

        if not text.strip():
            return [], []
        payload: dict[str, Any] = json.loads(text)
        findings: list[Finding] = []
        metadata: list[dict[str, Any]] = []
        for file_name, records in (payload.get("results") or {}).items():
            for record in records:
                if not isinstance(record, dict):
                    continue
                detector = str(record.get("type", "Secret"))
                line_number = int(record.get("line_number", 0) or 0)
                metadata.append(
                    {
                        "scanner": "detect-secrets",
                        "detector": detector,
                        "file": str(file_name),
                        "line": line_number,
                    }
                )
                findings.append(
                    Finding(
                        title=f"Potential secret detected: {detector}",
                        severity=Severity.MEDIUM,
                        asset=asset.name,
                        stage="secrets",
                        rule_id=f"detect-secrets:{detector}",
                        root_cause="committed_credentials",
                        location=Location(file=str(file_name), line=line_number),
                        description="detect-secrets identified credential-like material.",
                        evidence=f"detector={detector}",
                        confidence=0.7,
                    )
                )
        return findings, metadata

    @staticmethod
    def _dedupe_findings(findings: list[Finding]) -> list[Finding]:
        """Collapse overlapping history/filesystem scanner results without hiding confidence."""

        unique: dict[tuple[str, str, int], Finding] = {}
        for finding in findings:
            key = (
                finding.rule_id,
                finding.location.file.replace("\\", "/"),
                finding.location.line,
            )
            current = unique.get(key)
            if current is None or finding.confidence > current.confidence:
                unique[key] = finding
        return list(unique.values())

    @staticmethod
    def _dedupe_metadata(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Collapse metadata-only duplicates while preferring verified TruffleHog records."""

        unique: dict[tuple[str, str, str, int], dict[str, Any]] = {}
        for record in records:
            key = (
                str(record.get("scanner", "")),
                str(record.get("detector", "")),
                str(record.get("file", "")).replace("\\", "/"),
                int(record.get("line", 0) or 0),
            )
            current = unique.get(key)
            if current is None or bool(record.get("verified")) > bool(current.get("verified")):
                unique[key] = record
        return list(unique.values())

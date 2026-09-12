"""Stage 5: secret scanning with secret-value suppression."""

from __future__ import annotations

import asyncio
import json
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
            completed = self._tool(
                ["trufflehog", "git", asset.path.as_uri(), "--json"],
                cwd=asset.path,
                timeout_s=900,
            )
            scanner_findings, scanner_metadata = self._parse_trufflehog_text(completed.stdout, asset)
            findings.extend(scanner_findings)
            sanitized.extend(scanner_metadata)

        if self.tool_runner.available("detect-secrets"):
            completed = self._tool(
                ["detect-secrets", "scan", str(asset.path), "--all-files"],
                cwd=asset.path,
                timeout_s=900,
            )
            scanner_findings, scanner_metadata = self._parse_detect_secrets_text(
                completed.stdout,
                asset,
            )
            findings.extend(scanner_findings)
            sanitized.extend(scanner_metadata)

        (output_dir / "secret-findings-sanitized.json").write_text(
            json.dumps(sanitized, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return findings

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
            file_name = str(git_data.get("file", "")) if isinstance(git_data, dict) else ""
            line_number = int(git_data.get("line", 0) or 0) if isinstance(git_data, dict) else 0
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

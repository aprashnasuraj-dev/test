"""Stage 5: secret scanning with secret-value suppression."""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from ens_audit.config import RESULTS_DIR
from ens_audit.models import Asset, Finding, Location, Severity


class SecretStage:
    """Run TruffleHog and detect-secrets without retaining discovered secret values.

    Security invariant: raw secret values are never copied into normalized findings, logs,
    evidence, or report data.
    """

    async def run(self, asset: Asset) -> list[Finding]:
        """Scan one asset for committed or present secret material."""

        return await asyncio.to_thread(self._run_sync, asset)

    def _run_sync(self, asset: Asset) -> list[Finding]:
        """Execute available secret scanners and normalize metadata-only findings."""

        output_dir = RESULTS_DIR / asset.name / "secrets"
        output_dir.mkdir(parents=True, exist_ok=True)
        findings: list[Finding] = []

        if shutil.which("trufflehog"):
            completed = self._tool(
                ["trufflehog", "git", asset.path.as_uri(), "--json"],
                cwd=asset.path,
                timeout_s=900,
            )
            raw_path = output_dir / "trufflehog.jsonl"
            raw_path.write_text(completed.stdout, encoding="utf-8")
            findings.extend(self._parse_trufflehog(raw_path, asset))

        if shutil.which("detect-secrets"):
            completed = self._tool(
                ["detect-secrets", "scan", str(asset.path), "--all-files"],
                cwd=asset.path,
                timeout_s=900,
            )
            raw_path = output_dir / "detect-secrets.json"
            raw_path.write_text(completed.stdout, encoding="utf-8")
            findings.extend(self._parse_detect_secrets(raw_path, asset))

        return findings

    @staticmethod
    def _tool(argv: list[str], *, cwd: Path, timeout_s: int) -> subprocess.CompletedProcess[str]:
        """Run a secret scanner without shell interpretation."""

        completed = subprocess.run(
            argv,
            cwd=cwd,
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or "secret scanner failed"
            raise RuntimeError(f"{argv[0]} failed: {detail[:2000]}")
        return completed

    @staticmethod
    def _parse_trufflehog(path: Path, asset: Asset) -> list[Finding]:
        """Normalize TruffleHog JSON-lines records while discarding raw secret fields."""

        findings: list[Finding] = []
        if not path.exists():
            return findings
        for line in path.read_text(encoding="utf-8").splitlines():
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
            findings.append(
                Finding(
                    title=f"Potential secret detected: {detector}",
                    severity=Severity.HIGH if verified else Severity.MEDIUM,
                    asset=asset.name,
                    stage="secrets",
                    rule_id=f"trufflehog:{detector}",
                    root_cause="committed-credential",
                    location=Location(file=file_name, line=line_number),
                    description="Secret scanner identified credential-like material.",
                    evidence=f"detector={detector}; verified={verified}",
                    confidence=1.0 if verified else 0.7,
                )
            )
        return findings

    @staticmethod
    def _parse_detect_secrets(path: Path, asset: Asset) -> list[Finding]:
        """Normalize detect-secrets results without retaining matched values."""

        if not path.exists() or not path.read_text(encoding="utf-8").strip():
            return []
        payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        findings: list[Finding] = []
        for file_name, records in (payload.get("results") or {}).items():
            for record in records:
                if not isinstance(record, dict):
                    continue
                detector = str(record.get("type", "Secret"))
                findings.append(
                    Finding(
                        title=f"Potential secret detected: {detector}",
                        severity=Severity.MEDIUM,
                        asset=asset.name,
                        stage="secrets",
                        rule_id=f"detect-secrets:{detector}",
                        root_cause="committed-credential",
                        location=Location(
                            file=str(file_name),
                            line=int(record.get("line_number", 0) or 0),
                        ),
                        description="detect-secrets identified credential-like material.",
                        evidence=f"detector={detector}",
                        confidence=0.7,
                    )
                )
        return findings

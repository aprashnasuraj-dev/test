"""Stage 3: bounded property fuzzing for Solidity-bearing assets."""

from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any

from ens_audit.config import RESULTS_DIR
from ens_audit.models import Asset, Finding, Location, Severity
from ens_audit.tooling import DEFAULT_TOOL_RUNNER


class FuzzStage:
    """Run available property fuzzers with deterministic, bounded settings.

    Security invariant: fuzzers execute only inside the checked-out asset directory with
    fixed argv tokens and no shell interpretation. TypeScript fast-check is intentionally
    not invoked unless the target repository provides a real property-test harness.
    """

    def __init__(self) -> None:
        self.tool_runner = DEFAULT_TOOL_RUNNER

    async def run(self, asset: Asset) -> list[Finding]:
        """Execute applicable fuzzers and return normalized invariant failures."""

        return await asyncio.to_thread(self._run_sync, asset)

    def _run_sync(self, asset: Asset) -> list[Finding]:
        """Run the bounded fuzz workflow for one asset."""

        output_dir = RESULTS_DIR / asset.name / "fuzz"
        output_dir.mkdir(parents=True, exist_ok=True)
        findings: list[Finding] = []

        if asset.has_solidity and self.tool_runner.available("forge"):
            forge_output = output_dir / "foundry-fuzz.json"
            completed = self._tool(
                [
                    "forge",
                    "test",
                    "--match-test",
                    "invariant",
                    "--fuzz-runs",
                    "100000",
                    "--json",
                ],
                cwd=asset.path,
                timeout_s=2400,
                accepted_codes={0, 1},
            )
            forge_output.write_text(completed.stdout, encoding="utf-8")
            findings.extend(self._parse_forge(forge_output, asset))

        if asset.has_solidity and self.tool_runner.available("echidna"):
            config_path = output_dir / "echidna-config.yaml"
            config_path.write_text(
                "testLimit: 100000\nseqLen: 200\nshrinkLimit: 10000\n",
                encoding="utf-8",
            )
            completed = self._tool(
                ["echidna", str(asset.path), "--config", str(config_path)],
                cwd=asset.path,
                timeout_s=2400,
                accepted_codes={0, 1},
            )
            (output_dir / "echidna.txt").write_text(
                completed.stdout + completed.stderr,
                encoding="utf-8",
            )
            if completed.returncode == 1:
                findings.append(
                    self._failure(
                        asset,
                        "Echidna reported a property violation",
                        "echidna-property-violation",
                        completed.stdout + completed.stderr,
                    )
                )

        return findings

    def _tool(
        self,
        argv: list[str],
        *,
        cwd: Path,
        timeout_s: int,
        accepted_codes: set[int],
    ) -> subprocess.CompletedProcess[str]:
        """Run one fuzzer natively or through WSL as an argv-only subprocess."""

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
    def _parse_forge(path: Path, asset: Asset) -> list[Finding]:
        """Normalize explicit Foundry failure objects from JSON output."""

        if not path.exists() or not path.read_text(encoding="utf-8").strip():
            return []
        try:
            payload: Any = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        findings: list[Finding] = []
        records = payload.values() if isinstance(payload, dict) else payload
        for record in records:
            if not isinstance(record, dict):
                continue
            status = str(record.get("status", record.get("test_status", ""))).lower()
            if status not in {"failure", "failed", "fail"}:
                continue
            name = str(record.get("name", record.get("test", "Foundry invariant")))
            findings.append(
                FuzzStage._failure(
                    asset,
                    f"Foundry invariant failed: {name}",
                    "foundry-invariant",
                    json.dumps(record),
                )
            )
        return findings

    @staticmethod
    def _failure(asset: Asset, title: str, rule_id: str, evidence: str) -> Finding:
        """Build a normalized property-violation finding."""

        return Finding(
            title=title,
            severity=Severity.HIGH,
            asset=asset.name,
            stage="fuzz",
            rule_id=rule_id,
            root_cause="property-violation",
            location=Location(file=""),
            description=title,
            evidence=evidence[:12000],
            confidence=1.0,
        )

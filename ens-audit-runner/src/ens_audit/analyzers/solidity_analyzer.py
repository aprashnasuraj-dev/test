"""Conservative source-only checks for Solidity code."""

from __future__ import annotations

import re
from pathlib import Path

from ens_audit.models import Asset, Finding, Location, Severity

_RULES: tuple[tuple[str, re.Pattern[str], Severity, str, str], ...] = (
    (
        "solidity-delegatecall",
        re.compile(r"\.delegatecall\s*\("),
        Severity.HIGH,
        "delegatecall_surface",
        "delegatecall can execute foreign code in the caller's storage context; verify target control and authorization.",
    ),
    (
        "solidity-tx-origin",
        re.compile(r"\btx\.origin\b"),
        Severity.MEDIUM,
        "tx_origin_authorization",
        "tx.origin is present; verify it is not used as an authorization primitive.",
    ),
    (
        "solidity-selfdestruct",
        re.compile(r"\bselfdestruct\s*\("),
        Severity.HIGH,
        "destructive_contract_operation",
        "selfdestruct is reachable in source; verify access control and deployment assumptions.",
    ),
    (
        "solidity-low-level-call",
        re.compile(r"\.call\s*\{"),
        Severity.MEDIUM,
        "low_level_external_call",
        "Low-level call found; verify return handling, reentrancy boundaries, and target control.",
    ),
)


class SolidityAnalyzer:
    """Scan Solidity text for security-sensitive primitives without executing contracts.

    Security invariant: source files are read as inert text and only fixed regex rules are
    applied.
    """

    def analyze(self, asset: Asset) -> list[Finding]:
        """Analyze all non-symlink Solidity files below one asset root."""

        findings: list[Finding] = []
        for path in sorted(asset.path.rglob("*.sol")):
            if path.is_symlink():
                continue
            findings.extend(self._analyze_file(asset, path))
        return findings

    @staticmethod
    def _analyze_file(asset: Asset, path: Path) -> list[Finding]:
        """Apply fixed source rules to one Solidity file."""

        findings: list[Finding] = []
        for number, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(),
            start=1,
        ):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            for rule_id, pattern, severity, root_cause, description in _RULES:
                if not pattern.search(line):
                    continue
                findings.append(
                    Finding(
                        title=description.split(";")[0],
                        severity=severity,
                        asset=asset.name,
                        stage="sast",
                        rule_id=rule_id,
                        root_cause=root_cause,
                        location=Location(
                            file=str(path.relative_to(asset.path)),
                            line=number,
                        ),
                        description=description,
                        evidence=stripped[:2000],
                        confidence=0.55,
                    )
                )
        return findings

"""Lightweight source-only taint analysis for TypeScript and JavaScript."""

from __future__ import annotations

import re
from pathlib import Path

from ens_audit.models import Asset, Finding, Location, Severity

_SOURCE = re.compile(
    r"(?:URLSearchParams|localStorage\.(?:getItem|setItem)|sessionStorage\.getItem|"
    r"request\.(?:url|from|chainId)|notification\.(?:data|url)|event\.data)"
)
_ASSIGN = re.compile(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(.+)")
_PROPAGATE = re.compile(r"\b([A-Za-z_$][\w$]*)\s*=\s*([A-Za-z_$][\w$]*)\b")
_SINKS: tuple[tuple[str, re.Pattern[str], str, Severity], ...] = (
    ("untrusted-network-url", re.compile(r"\b(?:fetch|axios(?:\.get)?|https?\.get)\s*\(([^)]*)"), "untrusted_url_to_network_sink", Severity.HIGH),
    ("untrusted-navigation-url", re.compile(r"\b(?:open|window\.open|clients\.openWindow)\s*\(([^)]*)"), "unvalidated_navigation_url", Severity.MEDIUM),
    ("untrusted-postmessage-target", re.compile(r"\.postMessage\s*\(([^)]*)"), "unvalidated_postmessage_target", Severity.MEDIUM),
    ("request-from-to-signer", re.compile(r"\b(?:sign|sendTransaction|account)\w*\s*\(([^)]*)"), "request_from_not_bound_to_signer", Severity.HIGH),
)


class TypeScriptAnalyzer:
    """Perform conservative line-oriented taint tracking without executing source code.

    Security invariant: analysis reads text only, never imports or evaluates the audited
    repository, and emits findings only when a tainted identifier reaches a modeled sink.
    """

    def analyze(self, asset: Asset) -> list[Finding]:
        """Analyze all non-symlink TS/JS source files below one asset root."""

        findings: list[Finding] = []
        for path in self._source_files(asset.path):
            findings.extend(self._analyze_file(asset, path))
        return findings

    @staticmethod
    def _source_files(root: Path) -> list[Path]:
        """Return source files without following file symlinks or generated dependency trees."""

        files: list[Path] = []
        for suffix in ("*.ts", "*.tsx", "*.js", "*.jsx", "*.mjs", "*.cjs"):
            for path in root.rglob(suffix):
                if path.is_symlink() or "node_modules" in path.parts:
                    continue
                files.append(path)
        return sorted(set(files))

    def _analyze_file(self, asset: Asset, path: Path) -> list[Finding]:
        """Track tainted variables through simple assignments inside one source file."""

        text = path.read_text(encoding="utf-8", errors="replace")
        tainted: set[str] = set()
        findings: list[Finding] = []
        for number, line in enumerate(text.splitlines(), start=1):
            assignment = _ASSIGN.search(line)
            if assignment and self._expression_tainted(assignment.group(2), tainted):
                tainted.add(assignment.group(1))
            propagation = _PROPAGATE.search(line)
            if propagation and propagation.group(2) in tainted:
                tainted.add(propagation.group(1))
            for rule_id, sink, root_cause, severity in _SINKS:
                match = sink.search(line)
                if match and self._expression_tainted(match.group(1), tainted):
                    findings.append(
                        Finding(
                            title=f"Tainted input reaches {rule_id.replace('-', ' ')}",
                            severity=severity,
                            asset=asset.name,
                            stage="sast",
                            rule_id=f"custom-ts:{rule_id}",
                            root_cause=root_cause,
                            location=Location(
                                file=str(path.relative_to(asset.path)),
                                line=number,
                            ),
                            description="A modeled untrusted source reaches a sensitive sink without an observed sanitizer.",
                            evidence=line.strip()[:2000],
                            confidence=0.65,
                        )
                    )
        return findings

    @staticmethod
    def _expression_tainted(expression: str, tainted: set[str]) -> bool:
        """Return whether an expression contains a direct source or a tainted identifier."""

        if _SOURCE.search(expression):
            return True
        identifiers = set(re.findall(r"\b[A-Za-z_$][\w$]*\b", expression))
        return bool(identifiers & tainted)

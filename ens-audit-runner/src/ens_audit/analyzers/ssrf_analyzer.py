"""Source-only SSRF sink detection for JavaScript and TypeScript."""

from __future__ import annotations

import re
from pathlib import Path

from ens_audit.models import Asset, Finding, Location, Severity

_SINK = re.compile(r"\b(?:fetch|axios(?:\.get)?|https?\.get)\s*\(\s*([^,\)]+)")
_DYNAMIC_URL = re.compile(
    r"\b[\w$]*(?:url|uri|avatar|endpoint|target|href|src)[\w$]*\b",
    re.IGNORECASE,
)
_VALIDATION = re.compile(
    r"(?:new\s+URL|url\.protocol|hostname|host\b|isPrivate|isLoopback|ipaddr|ipaddress|allowlist|whitelist)",
    re.IGNORECASE,
)


class SSRFAnalyzer:
    """Detect dynamic outbound URL sinks lacking nearby destination validation.

    Security invariant: this analyzer only reads source text and never issues network requests.
    """

    def analyze(self, asset: Asset) -> list[Finding]:
        """Scan TS/JS source files for dynamic URL sinks without nearby validation."""

        findings: list[Finding] = []
        for path in self._files(asset.path):
            findings.extend(self._analyze_file(asset, path))
        return findings

    @staticmethod
    def _files(root: Path) -> list[Path]:
        """Return non-symlink JavaScript/TypeScript source files."""

        result: list[Path] = []
        for suffix in ("*.ts", "*.tsx", "*.js", "*.jsx", "*.mjs", "*.cjs"):
            result.extend(
                path
                for path in root.rglob(suffix)
                if not path.is_symlink() and "node_modules" not in path.parts
            )
        return sorted(set(result))

    @staticmethod
    def _analyze_file(asset: Asset, path: Path) -> list[Finding]:
        """Analyze one source file using a bounded local validation window.

        Security invariant: dynamic URL-like identifiers are recognized as complete source-code
        identifiers, including camelCase forms, without evaluating or requesting their values.
        """

        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        findings: list[Finding] = []
        for index, line in enumerate(lines):
            match = _SINK.search(line)
            if not match:
                continue
            argument = match.group(1).strip()
            if argument.startswith(("'", '"', "`")) and "${" not in argument:
                continue
            if not _DYNAMIC_URL.search(argument):
                continue
            start = max(0, index - 12)
            context = "\n".join(lines[start : index + 1])
            if _VALIDATION.search(context):
                continue
            findings.append(
                Finding(
                    title="Dynamic URL reaches outbound request without observed destination validation",
                    severity=Severity.HIGH,
                    asset=asset.name,
                    stage="sast",
                    rule_id="custom-ssrf:dynamic-url-sink",
                    root_cause="server_side_fetch_of_untrusted_avatar_url",
                    location=Location(
                        file=str(path.relative_to(asset.path)),
                        line=index + 1,
                    ),
                    description=(
                        "A variable URL-like value reaches an outbound request and no nearby "
                        "scheme, host, IP, or allowlist validation was observed."
                    ),
                    evidence=line.strip()[:2000],
                    confidence=0.7,
                )
            )
        return findings

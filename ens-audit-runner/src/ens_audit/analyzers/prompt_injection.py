"""Source-only detection of prompt-injection surfaces in LLM integrations."""

from __future__ import annotations

import re
from pathlib import Path

from ens_audit.models import Asset, Finding, Location, Severity

_LLM = re.compile(
    r"\b(?:openai|anthropic|chat\.completions|responses\.create|messages\.create)\b",
    re.IGNORECASE,
)
_UNTRUSTED = re.compile(
    r"\b(?:userInput|notes|description|content|body|request|issue|finding|source|repo|fileContent)\b"
)
_PROMPT = re.compile(r"\b(?:prompt|messages|system|user)\b", re.IGNORECASE)
_GUARD = re.compile(
    r"\b(?:sanitize|escape|untrusted_notes|untrusted_data|delimiter|structuredClone|JSON\.stringify)\b",
    re.IGNORECASE,
)
_PLAIN_STRING = re.compile(r'''(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')''')


class PromptInjectionAnalyzer:
    """Identify likely prompt construction from untrusted text without explicit separation.

    Security invariant: audited code is treated strictly as text and is never sent to an LLM
    by this analyzer.
    """

    def analyze(self, asset: Asset) -> list[Finding]:
        """Scan source files for LLM calls preceded by unsafe prompt construction."""

        findings: list[Finding] = []
        for path in self._files(asset.path):
            findings.extend(self._analyze_file(asset, path))
        return findings

    @staticmethod
    def _files(root: Path) -> list[Path]:
        """Return non-symlink Python/TS/JS source files."""

        files: list[Path] = []
        for suffix in ("*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.mjs", "*.cjs"):
            files.extend(
                path
                for path in root.rglob(suffix)
                if not path.is_symlink() and "node_modules" not in path.parts
            )
        return sorted(set(files))

    @staticmethod
    def _analyze_file(asset: Asset, path: Path) -> list[Finding]:
        """Analyze one file with a bounded context window around LLM calls.

        Security invariant: quoted static text is excluded from untrusted-token matching while
        template literals remain visible so interpolated identifiers cannot hide from detection.
        """

        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        findings: list[Finding] = []
        for index, line in enumerate(lines):
            if not _LLM.search(line):
                continue
            start = max(0, index - 30)
            context = "\n".join(lines[start : index + 1])
            code_context = _PLAIN_STRING.sub("", context)
            if not (_PROMPT.search(context) and _UNTRUSTED.search(code_context)):
                continue
            if _GUARD.search(context):
                continue
            findings.append(
                Finding(
                    title="Untrusted text appears to reach LLM prompt construction without explicit separation",
                    severity=Severity.MEDIUM,
                    asset=asset.name,
                    stage="sast",
                    rule_id="custom-llm:prompt-injection-surface",
                    root_cause="untrusted_prompt_content_not_separated",
                    location=Location(
                        file=str(path.relative_to(asset.path)),
                        line=index + 1,
                    ),
                    description=(
                        "An LLM call is near prompt/message construction that references untrusted "
                        "application or repository content, with no observed sanitizer or explicit "
                        "data delimiter."
                    ),
                    evidence="\n".join(lines[max(0, index - 4) : index + 1])[:4000],
                    confidence=0.6,
                )
            )
        return findings

"""Stage 6: conservative filtering of publicly disclosed known issues."""

from __future__ import annotations

import fnmatch
import hashlib
import re
from dataclasses import replace

from ens_audit.known_issues import KnownIssue, load_known_issues
from ens_audit.models import Finding, FindingStatus


class KnownIssueFilterStage:
    """Mark only same-root-cause findings as known duplicates.

    Security invariant: area or title similarity alone can never suppress a finding; asset
    scope and normalized root cause must match before any secondary matcher is considered.
    """

    def __init__(self, issues: tuple[KnownIssue, ...] | None = None) -> None:
        self.issues = issues if issues is not None else load_known_issues()

    async def run(self, findings: list[Finding]) -> list[Finding]:
        """Return findings with qualifying duplicates explicitly marked suppressed."""

        return [self._filter_one(finding) for finding in findings]

    def _filter_one(self, finding: Finding) -> Finding:
        """Suppress one finding only when a disclosed root cause is actually matched."""

        for issue in self.issues:
            if finding.asset not in issue.asset:
                continue
            if self._normalize_root(finding.root_cause) != self._normalize_root(issue.root_cause):
                continue
            if not self._matches_any_pattern(finding, issue):
                continue
            return replace(
                finding,
                status=FindingStatus.SUPPRESSED,
                suppressed_by=issue.id,
            )
        return finding

    @staticmethod
    def fingerprint(finding: Finding) -> str:
        """Return the root-cause fingerprint defined by the audit design.

        Security invariant: the digest uses only normalized path, function name, and CWE id,
        so evidence text or attacker-controlled scanner output cannot influence identity.
        """

        path = finding.location.file.replace("\\", "/").lower().strip()
        function = (finding.location.function or "").strip().lower()
        cwe = (finding.cwe or "").strip().upper()
        payload = f"{path}\x00{function}\x00{cwe}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def _matches_any_pattern(self, finding: Finding, issue: KnownIssue) -> bool:
        """Check narrow matcher conditions after root-cause equality is established."""

        if not issue.match_patterns:
            return False
        haystack = "\n".join(
            (finding.title, finding.description, finding.evidence, finding.rule_id)
        )
        for pattern in issue.match_patterns:
            if pattern.file_glob and fnmatch.fnmatch(
                finding.location.file.replace("\\", "/"), pattern.file_glob
            ):
                return True
            if pattern.rule_id and fnmatch.fnmatch(finding.rule_id, pattern.rule_id):
                return True
            if pattern.cwe and finding.cwe and pattern.cwe.upper() == finding.cwe.upper():
                return True
            if pattern.function and finding.location.function == pattern.function:
                return True
            if pattern.content_regex and re.search(pattern.content_regex, haystack):
                return True
        return False

    @staticmethod
    def _normalize_root(value: str) -> str:
        """Normalize root-cause identifiers for strict semantic comparison."""

        return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")

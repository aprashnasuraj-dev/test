"""Stage 7: JSON, Markdown, and Immunefi-format report generation."""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Iterable

from ens_audit.config import ACTIVE_UPSTREAM_COMMIT, RESULTS_DIR
from ens_audit.models import AuditReport, Finding, FindingStatus, Severity


class ReportStage:
    """Generate inert report artifacts from normalized findings.

    Security invariant: finding text is written only as report data; filenames are sanitized
    and no report content is evaluated or executed.
    """

    async def generate(self, results: dict[str, list[Finding]]) -> AuditReport:
        """Generate all required report formats from per-asset findings."""

        return await asyncio.to_thread(self._generate_sync, results)

    def _generate_sync(self, results: dict[str, list[Finding]]) -> AuditReport:
        """Write JSON, aggregate Markdown, and individual Immunefi submissions."""

        output_dir = RESULTS_DIR / "report"
        submissions_dir = output_dir / "findings"
        submissions_dir.mkdir(parents=True, exist_ok=True)
        for stale in submissions_dir.glob("*.md"):
            if stale.is_file() and not stale.is_symlink():
                stale.unlink()

        findings = [finding for asset_findings in results.values() for finding in asset_findings]
        completed = tuple(
            sorted({finding.stage for finding in findings} | {"known_filter", "report"})
        )
        json_payload = {
            "commit": ACTIVE_UPSTREAM_COMMIT,
            "completed_stages": list(completed),
            "findings": [finding.to_dict() for finding in findings],
        }
        (output_dir / "audit-report.json").write_text(
            json.dumps(json_payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (output_dir / "audit-report.md").write_text(
            self._aggregate_markdown(findings),
            encoding="utf-8",
        )

        for index, finding in enumerate(findings, start=1):
            if finding.status is not FindingStatus.OPEN:
                continue
            name = self._safe_filename(f"{index:03d}-{finding.asset}-{finding.title}") + ".md"
            (submissions_dir / name).write_text(
                self._immunefi_markdown(finding),
                encoding="utf-8",
            )

        return AuditReport(
            commit=ACTIVE_UPSTREAM_COMMIT,
            findings=tuple(findings),
            completed_stages=completed,
            output_dir=output_dir,
        )

    @staticmethod
    def _aggregate_markdown(findings: list[Finding]) -> str:
        """Build a human-readable Markdown report grouped by severity."""

        open_findings = [finding for finding in findings if finding.status is FindingStatus.OPEN]
        suppressed = [finding for finding in findings if finding.status is FindingStatus.SUPPRESSED]
        lines = [
            "# ENS Audit Report",
            "",
            f"Audited commit: `{ACTIVE_UPSTREAM_COMMIT}`",
            "",
            f"Open findings: **{len(open_findings)}**  ",
            f"Suppressed known issues: **{len(suppressed)}**",
            "",
        ]
        for severity in (
            Severity.CRITICAL,
            Severity.HIGH,
            Severity.MEDIUM,
            Severity.LOW,
            Severity.INFO,
        ):
            group = [finding for finding in open_findings if finding.severity is severity]
            lines.extend([f"## {severity.value}", ""])
            if not group:
                lines.extend(["None.", ""])
                continue
            for finding in group:
                lines.extend(
                    [
                        f"### {finding.title}",
                        "",
                        f"- Asset: `{finding.asset}`",
                        f"- Stage: `{finding.stage}`",
                        f"- Rule: `{finding.rule_id}`",
                        f"- Location: `{finding.location.file}:{finding.location.line}`",
                        f"- Root cause: `{finding.root_cause}`",
                        "",
                        finding.description,
                        "",
                    ]
                )
        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _immunefi_markdown(finding: Finding) -> str:
        """Render one unsuppressed finding in the requested Immunefi submission layout."""

        impact = finding.impact or "Impact requires reviewer confirmation from the supplied trace."
        recommendation = finding.recommendation or (
            "Add a fail-closed validation at the identified trust boundary and add a regression test."
        )
        references = "\n".join(f"- {value}" for value in finding.references) or "- None recorded"
        return "\n".join(
            [
                f"# {finding.title}",
                "",
                "## Severity",
                finding.severity.value,
                "",
                "## Asset affected",
                finding.asset,
                "",
                "## Root cause",
                finding.root_cause,
                "",
                "## Proof of Concept (code trace)",
                "```text",
                ReportStage._fence_safe(finding.evidence),
                "```",
                "",
                "## Impact",
                impact,
                "",
                "## Recommendation",
                recommendation,
                "",
                "## References",
                references,
                "",
            ]
        )

    @staticmethod
    def _safe_filename(value: str) -> str:
        """Return a Windows-safe bounded filename stem."""

        cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "-", value).strip(" .-")
        cleaned = re.sub(r"\s+", "-", cleaned)
        return cleaned[:140] or "finding"

    @staticmethod
    def _fence_safe(value: str) -> str:
        """Prevent finding evidence from closing the Markdown code fence."""

        return value.replace("```", "` ` `")[:20000]


def count_open(findings: Iterable[Finding]) -> int:
    """Return the number of findings still eligible for review/submission."""

    return sum(1 for finding in findings if finding.status is FindingStatus.OPEN)

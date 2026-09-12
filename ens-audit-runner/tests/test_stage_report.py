"""Tests for aggregate and per-finding report generation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ens_audit.models import Finding, FindingStatus, Location, Severity
from ens_audit.pipeline.stage_report import ReportStage, count_open


def _finding(
    *,
    title: str,
    severity: Severity,
    status: FindingStatus = FindingStatus.OPEN,
    suppressed_by: str | None = None,
    impact: str = "",
    recommendation: str = "",
    references: tuple[str, ...] = (),
) -> Finding:
    """Build one normalized report-stage finding."""

    return Finding(
        title=title,
        severity=severity,
        asset="manager",
        stage="sast",
        rule_id="rule-id",
        root_cause="example_root",
        location=Location("src/example.ts", 7),
        description="example description",
        evidence="trace ``` marker",
        impact=impact,
        recommendation=recommendation,
        references=references,
        status=status,
        suppressed_by=suppressed_by,
    )


@pytest.mark.asyncio
async def test_generate_writes_metadata_and_open_only_submission(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Aggregate output preserves all findings while submissions include only open records."""

    monkeypatch.setattr("ens_audit.pipeline.stage_report.RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr("ens_audit.pipeline.stage_report.ACTIVE_UPSTREAM_COMMIT", "c" * 40)

    findings_dir = tmp_path / "results/report/findings"
    findings_dir.mkdir(parents=True)
    stale = findings_dir / "stale.md"
    stale.write_text("old", encoding="utf-8")

    open_finding = _finding(
        title='Unsafe <target>: "owner"?',
        severity=Severity.HIGH,
        impact="Direct theft of user funds.",
        recommendation="Bind the signer before execution.",
        references=("commit:c", "src/example.ts:7"),
    )
    suppressed = _finding(
        title="Known issue",
        severity=Severity.MEDIUM,
        status=FindingStatus.SUPPRESSED,
        suppressed_by="R2-01",
    )
    false_positive = _finding(
        title="False positive",
        severity=Severity.LOW,
        status=FindingStatus.FALSE_POSITIVE,
    )

    report = await ReportStage().generate(
        {"manager": [open_finding, suppressed, false_positive]}
    )

    assert report.commit == "c" * 40
    assert report.completed_stages == ("known_filter", "report", "sast")
    assert len(report.findings) == 3
    assert stale.exists() is False

    payload = json.loads((report.output_dir / "audit-report.json").read_text(encoding="utf-8"))
    assert payload["commit"] == "c" * 40
    assert len(payload["findings"]) == 3

    aggregate = (report.output_dir / "audit-report.md").read_text(encoding="utf-8")
    assert "Open findings: **1**" in aggregate
    assert "Suppressed known issues: **1**" in aggregate
    assert "## Critical\n\nNone." in aggregate
    assert "Unsafe <target>" in aggregate

    submissions = list(findings_dir.glob("*.md"))
    assert len(submissions) == 1
    submission = submissions[0].read_text(encoding="utf-8")
    assert "Direct theft of user funds." in submission
    assert "Bind the signer before execution." in submission
    assert "- commit:c" in submission
    assert "trace ` ` ` marker" in submission
    assert all(character not in submissions[0].name for character in '<>:"?')


def test_immunefi_markdown_uses_safe_fallbacks() -> None:
    """Missing impact, recommendation, and references render explicit review-safe fallbacks."""

    markdown = ReportStage._immunefi_markdown(
        _finding(title="Fallback", severity=Severity.MEDIUM)
    )
    assert "Impact requires reviewer confirmation" in markdown
    assert "Add a fail-closed validation" in markdown
    assert "- None recorded" in markdown


def test_safe_filename_is_bounded_and_has_empty_fallback() -> None:
    """Windows-invalid characters are removed and filename stems remain bounded."""

    assert ReportStage._safe_filename('  <>:"/\\|?*  ') == "finding"
    safe = ReportStage._safe_filename("x" * 200)
    assert len(safe) == 140


def test_fence_safe_escapes_markers_and_bounds_evidence() -> None:
    """Finding evidence cannot close the generated Markdown fence or grow unbounded."""

    safe = ReportStage._fence_safe("```" + ("x" * 25000))
    assert safe.startswith("` ` `")
    assert len(safe) == 20000


def test_count_open_excludes_suppressed_and_false_positive() -> None:
    """Submission counts include only findings still open for review."""

    findings = [
        _finding(title="open", severity=Severity.HIGH),
        _finding(
            title="suppressed",
            severity=Severity.MEDIUM,
            status=FindingStatus.SUPPRESSED,
            suppressed_by="R3-02",
        ),
        _finding(
            title="false-positive",
            severity=Severity.LOW,
            status=FindingStatus.FALSE_POSITIVE,
        ),
    ]
    assert count_open(findings) == 1

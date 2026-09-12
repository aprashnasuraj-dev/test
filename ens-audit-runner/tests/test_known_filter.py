"""Tests for root-cause-safe known-issue suppression."""

from __future__ import annotations

import pytest

from ens_audit.known_issues import load_known_issues
from ens_audit.known_issues.registry import KnownIssue, MatchPattern
from ens_audit.models import Finding, FindingStatus, Location, Severity
from ens_audit.pipeline.stage_known_filter import KnownIssueFilterStage


def _finding(
    *,
    asset: str = "transaction-manager",
    rule_id: str = "ens-xstate-missing-complete",
    root_cause: str = "xstate_subscription_missing_completion",
    file: str = "src/machines/example.ts",
    function: str | None = "waitForActor",
    cwe: str | None = "CWE-754",
    description: str = "subscription has next without complete",
    evidence: str = "actor.subscribe({ next: resolve })",
) -> Finding:
    """Build a representative analyzer finding for filter tests."""

    return Finding(
        title="XState actor subscription handles next but not completion",
        severity=Severity.HIGH,
        asset=asset,
        stage="sast",
        rule_id=rule_id,
        root_cause=root_cause,
        location=Location(file, 42, 1, function),
        description=description,
        evidence=evidence,
        cwe=cwe,
    )


def _issue(*patterns: MatchPattern, root_cause: str = "example_root") -> KnownIssue:
    """Build one tightly scoped known issue for matcher branch tests."""

    return KnownIssue(
        id="TEST-01",
        severity="Medium",
        asset=("transaction-manager",),
        title="test issue",
        root_cause=root_cause,
        match_patterns=patterns,
    )


def test_registry_loads_complete_public_disclosure() -> None:
    """Packaged registry must retain security, QA, Manager WEB, and Explorer WEB IDs."""

    issues = load_known_issues()
    ids = {issue.id for issue in issues}
    assert len(issues) >= 60
    assert len(ids) == len(issues)
    assert {
        "R2-01",
        "SEC-MGR-003",
        "R3-02",
        "R3-08",
        "QA-01",
        "QA-10",
        "WEB-806",
        "WEB-1304",
        "WEB-1257",
        "WEB-580",
    } <= ids


@pytest.mark.asyncio
async def test_same_root_cause_and_rule_is_suppressed() -> None:
    """A disclosed root cause with a matching narrow rule is marked suppressed."""

    stage = KnownIssueFilterStage()
    [result] = await stage.run([_finding()])
    assert result.status is FindingStatus.SUPPRESSED
    assert result.suppressed_by == "R3-02"


@pytest.mark.asyncio
async def test_same_area_but_different_root_cause_stays_open() -> None:
    """A bypass/new mechanism in the same code area must remain reportable."""

    stage = KnownIssueFilterStage()
    [result] = await stage.run([_finding(root_cause="new_actor_race_condition")])
    assert result.status is FindingStatus.OPEN
    assert result.suppressed_by is None


@pytest.mark.asyncio
async def test_same_rule_on_wrong_asset_stays_open() -> None:
    """A similarly named issue outside the disclosed asset scope must not be suppressed."""

    stage = KnownIssueFilterStage()
    [result] = await stage.run([_finding(asset="manager")])
    assert result.status is FindingStatus.OPEN


def test_fingerprint_is_stable_across_path_separator_case() -> None:
    """Root-cause fingerprints normalize source path separators and case."""

    left = _finding()
    right = Finding(
        title=left.title,
        severity=left.severity,
        asset=left.asset,
        stage=left.stage,
        rule_id=left.rule_id,
        root_cause=left.root_cause,
        location=Location("SRC\\MACHINES\\EXAMPLE.TS", 99, 9, "waitForActor"),
        description=left.description,
        evidence="different evidence",
        cwe=left.cwe,
    )
    assert KnownIssueFilterStage.fingerprint(left) == KnownIssueFilterStage.fingerprint(right)


@pytest.mark.parametrize(
    ("pattern", "finding"),
    [
        (MatchPattern(file_glob="src/machines/*.ts"), _finding(root_cause="example_root")),
        (MatchPattern(rule_id="ens-*"), _finding(root_cause="example_root")),
        (MatchPattern(cwe="cwe-754"), _finding(root_cause="example_root")),
        (MatchPattern(function="waitForActor"), _finding(root_cause="example_root")),
        (
            MatchPattern(content_regex=r"next without complete"),
            _finding(root_cause="example_root"),
        ),
    ],
)
def test_each_narrow_matcher_can_match(pattern: MatchPattern, finding: Finding) -> None:
    """Each supported structural matcher can independently identify the disclosed mechanism."""

    stage = KnownIssueFilterStage((_issue(pattern),))
    assert stage._matches_any_pattern(finding, stage.issues[0]) is True


def test_empty_match_patterns_never_suppress() -> None:
    """Root-cause equality alone is insufficient when a disclosure has no structural matcher."""

    finding = _finding(root_cause="example_root")
    stage = KnownIssueFilterStage((_issue(),))
    assert stage._matches_any_pattern(finding, stage.issues[0]) is False
    assert stage._filter_one(finding).status is FindingStatus.OPEN


def test_nonmatching_structural_patterns_remain_open() -> None:
    """A same-root finding stays open when none of the narrow structural matchers apply."""

    finding = _finding(
        root_cause="example_root",
        file="src/other.ts",
        rule_id="different-rule",
        function="differentFunction",
        cwe=None,
        description="different behavior",
        evidence="no disclosed pattern",
    )
    issue = _issue(
        MatchPattern(file_glob="src/machines/*.ts"),
        MatchPattern(rule_id="ens-*"),
        MatchPattern(cwe="CWE-754"),
        MatchPattern(function="waitForActor"),
        MatchPattern(content_regex=r"next without complete"),
    )
    stage = KnownIssueFilterStage((issue,))
    assert stage._filter_one(finding).status is FindingStatus.OPEN


def test_root_cause_normalization_is_format_insensitive() -> None:
    """Punctuation/case differences in the same root-cause label normalize identically."""

    assert KnownIssueFilterStage._normalize_root("Actor Subscribe-Missing Completion") == (
        KnownIssueFilterStage._normalize_root("actor_subscribe_missing_completion")
    )

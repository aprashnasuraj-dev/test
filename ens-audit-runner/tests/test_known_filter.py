"""Tests for root-cause-safe known-issue suppression."""

from __future__ import annotations

import pytest

from ens_audit.known_issues import load_known_issues
from ens_audit.models import Finding, FindingStatus, Location, Severity
from ens_audit.pipeline.stage_known_filter import KnownIssueFilterStage


def _finding(
    *,
    asset: str = "transaction-manager",
    rule_id: str = "ens-xstate-missing-complete",
    root_cause: str = "xstate_subscription_missing_completion",
) -> Finding:
    """Build a representative analyzer finding for filter tests."""

    return Finding(
        title="XState actor subscription handles next but not completion",
        severity=Severity.HIGH,
        asset=asset,
        stage="sast",
        rule_id=rule_id,
        root_cause=root_cause,
        location=Location("src/machines/example.ts", 42, 1, "waitForActor"),
        description="subscription has next without complete",
        evidence="actor.subscribe({ next: resolve })",
        cwe="CWE-754",
    )


def test_registry_loads_public_security_issues() -> None:
    """Packaged registry must parse safely and retain unique disclosed identifiers."""

    issues = load_known_issues()
    ids = {issue.id for issue in issues}
    assert len(issues) >= 25
    assert len(ids) == len(issues)
    assert {"R2-01", "SEC-MGR-003", "R3-02", "R3-08"} <= ids


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

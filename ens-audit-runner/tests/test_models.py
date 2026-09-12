"""Tests for normalized audit domain models."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest

from ens_audit.models import Asset, Finding, FindingStatus, Location, Severity


def _finding(**overrides: object) -> Finding:
    """Build one valid finding for model tests."""

    values: dict[str, object] = {
        "title": "Example",
        "severity": Severity.HIGH,
        "asset": "manager",
        "stage": "sast",
        "rule_id": "rule",
        "root_cause": "root",
        "location": Location("src/example.ts", 12, 3, "run"),
        "description": "description",
        "evidence": "evidence",
    }
    values.update(overrides)
    return Finding(**values)  # type: ignore[arg-type]


def test_location_rejects_negative_coordinates() -> None:
    """Source coordinates must never be negative."""

    with pytest.raises(ValueError, match="non-negative"):
        Location("a.ts", -1, 0)


def test_finding_rejects_invalid_confidence() -> None:
    """Finding confidence is constrained to the closed unit interval."""

    with pytest.raises(ValueError, match="confidence"):
        _finding(confidence=1.01)


def test_suppressed_finding_requires_issue_id() -> None:
    """Suppression state requires an explicit disclosed issue reference."""

    with pytest.raises(ValueError, match="suppressed_by"):
        _finding(status=FindingStatus.SUPPRESSED)


def test_finding_serializes_to_json_safe_scalars() -> None:
    """Finding serialization converts enums and UUID values into scalar data."""

    finding = _finding(references=("https://example.invalid/reference",))
    payload = finding.to_dict()

    UUID(payload["id"])
    assert payload["severity"] == "High"
    assert payload["status"] == "open"
    assert payload["location"]["line"] == 12


def test_asset_is_immutable() -> None:
    """Audit asset identity cannot be mutated after validation."""

    asset = Asset("manager", Path("/tmp/manager"), "a" * 40)
    with pytest.raises((AttributeError, TypeError)):
        asset.name = "other"  # type: ignore[misc]

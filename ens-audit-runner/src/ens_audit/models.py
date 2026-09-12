"""Typed domain models shared by analyzers, storage, reports, and GUI views."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4


class Severity(StrEnum):
    """Supported finding severities ordered from informational to critical.

    Security invariant: findings may only use this closed severity vocabulary.
    """

    INFO = "Info"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class FindingStatus(StrEnum):
    """Triage state for a finding.

    Security invariant: suppression and false-positive state are explicit, never inferred
    from missing fields.
    """

    OPEN = "open"
    SUPPRESSED = "suppressed"
    FALSE_POSITIVE = "false_positive"


@dataclass(frozen=True, slots=True)
class Asset:
    """Represent one checked-out audit asset.

    Security invariant: ``path`` is a concrete local directory chosen by the downloader,
    not an arbitrary command fragment.
    """

    name: str
    path: Path
    commit: str
    has_solidity: bool = False


@dataclass(frozen=True, slots=True)
class Location:
    """Represent a source location without embedding source contents.

    Security invariant: line and column numbers are non-negative source coordinates.
    """

    file: str
    line: int = 0
    column: int = 0
    function: str | None = None

    def __post_init__(self) -> None:
        if self.line < 0 or self.column < 0:
            raise ValueError("line and column must be non-negative")


@dataclass(slots=True)
class Finding:
    """Normalized finding emitted by any audit stage.

    Security invariant: raw tool output is reduced to structured fields before storage or
    rendering; suppression never deletes the original finding record.
    """

    title: str
    severity: Severity
    asset: str
    stage: str
    rule_id: str
    root_cause: str
    location: Location
    description: str
    evidence: str
    impact: str = ""
    recommendation: str = ""
    references: tuple[str, ...] = ()
    cwe: str | None = None
    confidence: float = 1.0
    reproducer: str | None = None
    id: UUID = field(default_factory=uuid4)
    status: FindingStatus = FindingStatus.OPEN
    suppressed_by: str | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.status is FindingStatus.SUPPRESSED and not self.suppressed_by:
            raise ValueError("suppressed findings require suppressed_by")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the finding.

        Security invariant: filesystem objects and enums are converted to inert scalar data
        before crossing persistence or report boundaries.
        """

        payload = asdict(self)
        payload["id"] = str(self.id)
        payload["severity"] = self.severity.value
        payload["status"] = self.status.value
        return payload


@dataclass(frozen=True, slots=True)
class StageResult:
    """Capture one pipeline-stage execution result.

    Security invariant: command output is represented as data and is never executed by the
    GUI or report layer.
    """

    stage: str
    asset: str
    findings: tuple[Finding, ...]
    succeeded: bool
    duration_s: float
    log: str = ""


@dataclass(frozen=True, slots=True)
class AuditReport:
    """Represent the completed multi-asset audit.

    Security invariant: the report records the exact audited commit alongside findings.
    """

    commit: str
    findings: tuple[Finding, ...]
    completed_stages: tuple[str, ...]
    output_dir: Path

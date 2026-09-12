"""Dashboard tab for audit progress and severity triage."""

from __future__ import annotations

from collections import Counter
from typing import ClassVar

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPaintEvent
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ens_audit.config import ASSETS, PIPELINE_STAGES
from ens_audit.models import Finding, FindingStatus, Severity


class SeverityPie(QWidget):
    """Render open-finding severity proportions without external chart dependencies.

    Security invariant: only enum-keyed numeric counts influence drawing; finding text is never
    rendered or interpreted by the painter.
    """

    _COLORS: ClassVar[dict[Severity, QColor]] = {
        Severity.CRITICAL: QColor("#7f1d1d"),
        Severity.HIGH: QColor("#dc2626"),
        Severity.MEDIUM: QColor("#d97706"),
        Severity.LOW: QColor("#2563eb"),
        Severity.INFO: QColor("#64748b"),
    }

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an empty severity pie widget."""

        super().__init__(parent)
        self._counts = {severity: 0 for severity in Severity}
        self.setMinimumSize(180, 180)

    def set_counts(self, counts: dict[Severity, int]) -> None:
        """Replace pie data with non-negative counts for known severities."""

        self._counts = {severity: max(0, int(counts.get(severity, 0))) for severity in Severity}
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the current severity distribution."""

        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(12, 12, -12, -12)
        total = sum(self._counts.values())
        if total <= 0:
            painter.setPen(QColor("#64748b"))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "No open findings")
            return
        start = 0
        for severity in Severity:
            count = self._counts[severity]
            if count <= 0:
                continue
            span = round((count / total) * 5760)
            painter.setBrush(self._COLORS[severity])
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPie(rect, start, span)
            start += span


class Dashboard(QWidget):
    """Display audit completion and severity overview with run/export actions."""

    run_full_requested = Signal()
    run_selected_requested = Signal()
    export_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build dashboard controls and stage progress indicators."""

        super().__init__(parent)
        self.asset_label = QLabel(f"Assets: 0/{len(ASSETS)} Downloaded", self)
        self.stage_label = QLabel(f"Stages: 0/{len(PIPELINE_STAGES)} Complete", self)
        self.severity_labels = {
            severity: QLabel(f"{severity.value}: 0", self) for severity in Severity
        }
        self.stage_bars = {stage: QProgressBar(self) for stage in PIPELINE_STAGES}
        self.pie = SeverityPie(self)

        summary = QGroupBox("Audit Overview", self)
        summary_layout = QGridLayout(summary)
        summary_layout.addWidget(self.asset_label, 0, 0, 1, 2)
        summary_layout.addWidget(self.stage_label, 0, 2, 1, 2)
        for index, severity in enumerate(Severity):
            summary_layout.addWidget(self.severity_labels[severity], 1, index)

        stages = QGroupBox("Pipeline Progress", self)
        stages_layout = QGridLayout(stages)
        for row, stage in enumerate(PIPELINE_STAGES):
            bar = self.stage_bars[stage]
            bar.setRange(0, len(ASSETS))
            bar.setValue(0)
            stages_layout.addWidget(QLabel(stage.replace("_", " ").title(), self), row, 0)
            stages_layout.addWidget(bar, row, 1)

        run_full = QPushButton("Run Full Audit", self)
        run_full.clicked.connect(self.run_full_requested.emit)
        run_selected = QPushButton("Run Selected Stages", self)
        run_selected.clicked.connect(self.run_selected_requested.emit)
        export = QPushButton("Export Report", self)
        export.clicked.connect(self.export_requested.emit)
        actions = QHBoxLayout()
        actions.addWidget(run_full)
        actions.addWidget(run_selected)
        actions.addWidget(export)
        actions.addStretch(1)

        body = QHBoxLayout()
        body.addWidget(stages, 2)
        body.addWidget(self.pie, 1)

        layout = QVBoxLayout(self)
        layout.addWidget(summary)
        layout.addLayout(body)
        layout.addLayout(actions)
        layout.addStretch(1)

    def set_asset_count(self, downloaded: int) -> None:
        """Update downloaded-asset count with configured bounds."""

        count = min(max(0, int(downloaded)), len(ASSETS))
        self.asset_label.setText(f"Assets: {count}/{len(ASSETS)} Downloaded")

    def set_stage_progress(self, stage: str, completed_assets: int) -> None:
        """Update one known stage progress bar."""

        bar = self.stage_bars.get(stage)
        if bar is None:
            return
        bar.setValue(min(max(0, int(completed_assets)), len(ASSETS)))
        complete = sum(1 for value in self.stage_bars.values() if value.value() >= len(ASSETS))
        self.stage_label.setText(f"Stages: {complete}/{len(PIPELINE_STAGES)} Complete")

    def set_findings(self, findings: list[Finding]) -> None:
        """Update severity totals from open normalized findings."""

        counts = Counter(
            finding.severity for finding in findings if finding.status is FindingStatus.OPEN
        )
        normalized = {severity: counts.get(severity, 0) for severity in Severity}
        for severity, label in self.severity_labels.items():
            label.setText(f"{severity.value}: {normalized[severity]}")
        self.pie.set_counts(normalized)

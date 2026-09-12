"""Sortable, filterable finding triage view with contained source preview."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ens_audit.gui.widgets.code_preview import CodePreview
from ens_audit.models import Finding, FindingStatus, Severity


class FindingsView(QWidget):
    """Display, filter, inspect, and locally triage normalized findings.

    Security invariant: table and preview content are plain text; source preview paths are
    validated by ``CodePreview`` before filesystem access.
    """

    finding_updated = Signal(str)

    _HEADERS = ("#", "Severity", "Asset", "Stage", "Title", "File:Line", "Status")

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the finding filters, table, code preview, and triage controls.

        Security invariant: widgets hold finding IDs rather than executable callbacks sourced
        from scan output.
        """

        super().__init__(parent)
        self._findings: dict[UUID, Finding] = {}
        self._repo_roots: dict[str, Path] = {}

        self.asset_filter = QComboBox(self)
        self.severity_filter = QComboBox(self)
        self.stage_filter = QComboBox(self)
        self.status_filter = QComboBox(self)
        for combo in (self.asset_filter, self.severity_filter, self.stage_filter, self.status_filter):
            combo.addItem("All")
            combo.currentTextChanged.connect(self._rebuild_table)

        filters = QHBoxLayout()
        filters.addWidget(QLabel("Asset", self))
        filters.addWidget(self.asset_filter)
        filters.addWidget(QLabel("Severity", self))
        filters.addWidget(self.severity_filter)
        filters.addWidget(QLabel("Stage", self))
        filters.addWidget(self.stage_filter)
        filters.addWidget(QLabel("Status", self))
        filters.addWidget(self.status_filter)
        filters.addStretch(1)

        self.table = QTableWidget(0, len(self._HEADERS), self)
        self.table.setHorizontalHeaderLabels(self._HEADERS)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.itemSelectionChanged.connect(self._selection_changed)

        self.preview = CodePreview(self)
        self.notes = QPlainTextEdit(self)
        self.notes.setPlaceholderText("Analyst notes for the selected finding")
        self.notes.setMaximumHeight(90)
        self.notes.textChanged.connect(self._save_notes)

        self.suppress_button = QPushButton("Suppress", self)
        self.false_positive_button = QPushButton("Mark False Positive", self)
        self.reopen_button = QPushButton("Reopen", self)
        self.suppress_button.clicked.connect(self._suppress_selected)
        self.false_positive_button.clicked.connect(self._false_positive_selected)
        self.reopen_button.clicked.connect(self._reopen_selected)

        triage = QHBoxLayout()
        triage.addWidget(self.suppress_button)
        triage.addWidget(self.false_positive_button)
        triage.addWidget(self.reopen_button)
        triage.addStretch(1)

        lower = QWidget(self)
        lower_layout = QVBoxLayout(lower)
        lower_layout.setContentsMargins(0, 0, 0, 0)
        lower_layout.addWidget(QLabel("Code Preview", lower))
        lower_layout.addWidget(self.preview)
        lower_layout.addWidget(QLabel("Notes", lower))
        lower_layout.addWidget(self.notes)
        lower_layout.addLayout(triage)

        splitter = QSplitter(Qt.Orientation.Vertical, self)
        splitter.addWidget(self.table)
        splitter.addWidget(lower)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout(self)
        layout.addLayout(filters)
        layout.addWidget(splitter)

    def set_findings(self, findings: list[Finding], repo_roots: dict[str, Path]) -> None:
        """Replace the view model and audited repository roots.

        Security invariant: source roots are keyed by normalized asset name and used only by
        the contained preview component.
        """

        self._findings = {finding.id: finding for finding in findings}
        self._repo_roots = {name: path.resolve() for name, path in repo_roots.items()}
        self._reset_filter(self.asset_filter, sorted({finding.asset for finding in findings}))
        self._reset_filter(
            self.severity_filter,
            [severity.value for severity in Severity if any(f.severity is severity for f in findings)],
        )
        self._reset_filter(self.stage_filter, sorted({finding.stage for finding in findings}))
        self._reset_filter(self.status_filter, [status.value for status in FindingStatus])
        self._rebuild_table()

    def findings(self) -> list[Finding]:
        """Return the current normalized findings in stable insertion order.

        Security invariant: callers receive model objects only; no widget-owned executable
        state is exposed.
        """

        return list(self._findings.values())

    @staticmethod
    def _reset_filter(combo: QComboBox, values: list[str]) -> None:
        """Replace filter choices with inert plain strings.

        Security invariant: values are displayed as text only and cannot register actions.
        """

        current = combo.currentText()
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("All")
        combo.addItems(values)
        index = combo.findText(current)
        combo.setCurrentIndex(max(0, index))
        combo.blockSignals(False)

    def _rebuild_table(self) -> None:
        """Repopulate rows that satisfy all active filters.

        Security invariant: row identity is stored as a UUID string in Qt user data, never as
        source code or a callable.
        """

        selected_id = self._selected_id()
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        visible = [finding for finding in self._findings.values() if self._matches_filters(finding)]
        for index, finding in enumerate(visible, start=1):
            row = self.table.rowCount()
            self.table.insertRow(row)
            cells = (
                str(index),
                finding.severity.value,
                finding.asset,
                finding.stage,
                finding.title,
                f"{finding.location.file}:{finding.location.line}",
                finding.status.value,
            )
            for column, value in enumerate(cells):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, str(finding.id))
                self.table.setItem(row, column, item)
        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()
        if selected_id is not None:
            self._select_id(selected_id)

    def _matches_filters(self, finding: Finding) -> bool:
        """Return whether a finding matches the four current filter controls.

        Security invariant: comparisons are exact scalar equality checks only.
        """

        checks = (
            (self.asset_filter.currentText(), finding.asset),
            (self.severity_filter.currentText(), finding.severity.value),
            (self.stage_filter.currentText(), finding.stage),
            (self.status_filter.currentText(), finding.status.value),
        )
        return all(selected == "All" or selected == actual for selected, actual in checks)

    def _selected_id(self) -> UUID | None:
        """Return the selected finding UUID, rejecting malformed table data.

        Security invariant: arbitrary user-data strings that are not UUIDs are ignored.
        """

        items = self.table.selectedItems()
        if not items:
            return None
        value = items[0].data(Qt.ItemDataRole.UserRole)
        try:
            return UUID(str(value))
        except (TypeError, ValueError):
            return None

    def _selected_finding(self) -> Finding | None:
        """Resolve the selected UUID to the current finding model."""

        finding_id = self._selected_id()
        return self._findings.get(finding_id) if finding_id is not None else None

    def _selection_changed(self) -> None:
        """Refresh source preview and notes for the current row.

        Security invariant: source access occurs only through the path-contained preview API.
        """

        finding = self._selected_finding()
        if finding is None:
            self.preview.clear()
            self.notes.clear()
            return
        root = self._repo_roots.get(finding.asset)
        if root is not None:
            self.preview.show_location(root, finding.location)
        else:
            self.preview.setPlainText("Preview unavailable: repository root is not loaded.")
        self.notes.blockSignals(True)
        self.notes.setPlainText(finding.notes)
        self.notes.blockSignals(False)

    def _save_notes(self) -> None:
        """Persist analyst notes into the selected in-memory finding.

        Security invariant: notes remain plain text and are never evaluated by the GUI.
        """

        finding = self._selected_finding()
        if finding is None:
            return
        finding.notes = self.notes.toPlainText()[:10000]
        self.finding_updated.emit(str(finding.id))

    def _suppress_selected(self) -> None:
        """Mark the selected finding as manually suppressed with explicit provenance."""

        finding = self._selected_finding()
        if finding is None:
            return
        finding.status = FindingStatus.SUPPRESSED
        finding.suppressed_by = "manual"
        self._after_triage(finding)

    def _false_positive_selected(self) -> None:
        """Mark the selected finding as an analyst-classified false positive."""

        finding = self._selected_finding()
        if finding is None:
            return
        finding.status = FindingStatus.FALSE_POSITIVE
        finding.suppressed_by = None
        self._after_triage(finding)

    def _reopen_selected(self) -> None:
        """Return the selected finding to open triage state."""

        finding = self._selected_finding()
        if finding is None:
            return
        finding.status = FindingStatus.OPEN
        finding.suppressed_by = None
        self._after_triage(finding)

    def _after_triage(self, finding: Finding) -> None:
        """Refresh filters/table after a local triage change and emit its UUID."""

        finding_id = finding.id
        self.finding_updated.emit(str(finding_id))
        self._rebuild_table()
        self._select_id(finding_id)

    def _select_id(self, finding_id: UUID) -> None:
        """Select a visible row by validated finding UUID."""

        target = str(finding_id)
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == target:
                self.table.selectRow(row)
                return

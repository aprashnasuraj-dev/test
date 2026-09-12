"""Read-only browser for disclosed known issues."""

from __future__ import annotations

from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ens_audit.known_issues import load_known_issues


class KnownIssuesView(QWidget):
    """Display the validated known-issue registry used by suppression logic.

    Security invariant: registry fields are rendered as plain table text and cannot modify
    suppression rules at runtime.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Load the packaged registry into a read-only sortable table.

        Security invariant: data is sourced only through the safe YAML registry loader.
        """

        super().__init__(parent)
        self.table = QTableWidget(0, 6, self)
        self.table.setHorizontalHeaderLabels(
            ("ID", "Severity", "Assets", "Title", "Root Cause", "Notes")
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)

        for issue in load_known_issues():
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = (
                issue.id,
                issue.severity,
                ", ".join(issue.asset),
                issue.title,
                issue.root_cause,
                issue.notes,
            )
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)

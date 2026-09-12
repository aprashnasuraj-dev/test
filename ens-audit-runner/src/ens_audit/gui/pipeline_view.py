"""Pipeline tab for stage status, execution logs, and retry controls."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ens_audit.config import ASSETS, PIPELINE_STAGES

_ALLOWED_STATUS = {"pending", "running", "complete", "failed", "skipped", "paused"}


class PipelineView(QWidget):
    """Display per-stage execution state and bounded textual logs.

    Security invariant: scanner output is rendered as plain text and controls emit intent only;
    no button directly kills, spawns, or shells out to a process.
    """

    pause_requested = Signal()
    resume_requested = Signal()
    retry_failed_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build stage grid, controls, and a read-only log pane.

        Security invariant: stage rows are created only from configured assets and stages.
        """

        super().__init__(parent)
        self.table = QTableWidget(len(ASSETS) * len(PIPELINE_STAGES), 4, self)
        self.table.setHorizontalHeaderLabels(("Asset", "Stage", "Status", "Progress"))
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._row_by_key: dict[tuple[str, str], int] = {}

        row = 0
        for asset in ASSETS:
            for stage in PIPELINE_STAGES:
                self._row_by_key[(asset.name, stage)] = row
                self.table.setItem(row, 0, QTableWidgetItem(asset.name))
                self.table.setItem(row, 1, QTableWidgetItem(stage))
                self.table.setItem(row, 2, QTableWidgetItem("pending"))
                self.table.setItem(row, 3, QTableWidgetItem("0%"))
                row += 1

        self.logs = QPlainTextEdit(self)
        self.logs.setReadOnly(True)
        self.logs.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.logs.document().setMaximumBlockCount(10000)

        pause = QPushButton("Pause", self)
        resume = QPushButton("Resume", self)
        retry = QPushButton("Retry Failed Stages", self)
        pause.clicked.connect(self.pause_requested.emit)
        resume.clicked.connect(self.resume_requested.emit)
        retry.clicked.connect(self.retry_failed_requested.emit)

        controls = QHBoxLayout()
        controls.addWidget(pause)
        controls.addWidget(resume)
        controls.addWidget(retry)
        controls.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table, 2)
        layout.addLayout(controls)
        layout.addWidget(self.logs, 1)

    def set_stage_status(
        self,
        asset: str,
        stage: str,
        status: str,
        progress_percent: int = 0,
    ) -> None:
        """Update one configured stage row.

        Security invariant: unknown asset/stage/status values are ignored and progress is
        clamped to the closed 0..100 range.
        """

        row = self._row_by_key.get((asset, stage))
        if row is None or status not in _ALLOWED_STATUS:
            return
        bounded = min(max(0, int(progress_percent)), 100)
        self.table.setItem(row, 2, QTableWidgetItem(status))
        self.table.setItem(row, 3, QTableWidgetItem(f"{bounded}%"))

    def append_log(self, message: str) -> None:
        """Append a timestamped bounded log message as plain text.

        Security invariant: ANSI control bytes and excessive line length are removed before
        rendering so tool output cannot manipulate the terminal-like view.
        """

        cleaned = "".join(character for character in message if character >= " " or character == "\t")
        cleaned = cleaned[:4000]
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
        self.logs.appendPlainText(f"{timestamp}  {cleaned}")

    def failed_pairs(self) -> list[tuple[str, str]]:
        """Return configured asset/stage pairs currently marked failed.

        Security invariant: returned values originate only from the preconfigured stage grid.
        """

        failed: list[tuple[str, str]] = []
        for key, row in self._row_by_key.items():
            item = self.table.item(row, 2)
            if item is not None and item.text() == "failed":
                failed.append(key)
        return failed

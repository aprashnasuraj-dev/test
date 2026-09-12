"""Progress dialog used while audit stages execute."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QProgressBar, QVBoxLayout, QWidget


class ProgressDialog(QDialog):
    """Display bounded audit progress and expose a cancellation request.

    Security invariant: progress labels are rendered by Qt label text APIs only and are never
    interpreted as rich HTML from scanner output.
    """

    cancel_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the audit progress dialog.

        Security invariant: the dialog emits cancellation intent only; it never terminates
        worker threads or child processes directly.
        """

        super().__init__(parent)
        self.setWindowTitle("ENS Audit Progress")
        self.setModal(True)
        self.setMinimumWidth(460)

        self.status_label = QLabel("Preparing audit…", self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel, parent=self)
        buttons.rejected.connect(self._request_cancel)

        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(buttons)

    def update_progress(self, asset: str, stage: str, current: int, total: int) -> None:
        """Update progress from normalized pipeline counters.

        Security invariant: percentage calculation is clamped to 0..100 and never trusts a
        caller-supplied denominator of zero.
        """

        denominator = max(1, total)
        bounded_current = min(max(0, current), denominator)
        percent = int((bounded_current / denominator) * 100)
        self.progress_bar.setValue(percent)
        self.status_label.setText(f"{asset} — {stage} ({bounded_current}/{denominator})")

    def _request_cancel(self) -> None:
        """Emit a cooperative cancellation request and disable repeated clicks.

        Security invariant: cancellation is advisory and cannot kill unrelated processes.
        """

        self.cancel_requested.emit()
        self.status_label.setText("Cancellation requested…")

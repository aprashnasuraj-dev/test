"""Severity badge widget for findings and dashboard views."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget

from ens_audit.models import Severity


class SeverityBadge(QLabel):
    """Render a severity enum as a compact text badge.

    Security invariant: label content comes only from the closed ``Severity`` enum and rich
    text is disabled, so finding-controlled strings cannot inject markup into the widget.
    """

    _STYLES = {
        Severity.CRITICAL: "background:#7f1d1d;color:#ffffff;",
        Severity.HIGH: "background:#b91c1c;color:#ffffff;",
        Severity.MEDIUM: "background:#b45309;color:#ffffff;",
        Severity.LOW: "background:#1d4ed8;color:#ffffff;",
        Severity.INFO: "background:#475569;color:#ffffff;",
    }

    def __init__(self, severity: Severity, parent: QWidget | None = None) -> None:
        """Initialize a badge from a validated severity.

        Security invariant: ``severity`` must be an enum member; arbitrary text is rejected.
        """

        if not isinstance(severity, Severity):
            raise TypeError("severity must be a Severity")
        super().__init__(severity.value.upper(), parent)
        self.setTextFormat(Qt.TextFormat.PlainText)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            self._STYLES[severity]
            + "padding:3px 8px;border-radius:7px;font-weight:600;"
        )
        self.setMinimumWidth(72)

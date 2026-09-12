"""Coverage tests for the severity badge widget."""

from __future__ import annotations

import os
from typing import cast

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ens_audit.gui.widgets.severity_badge import SeverityBadge
from ens_audit.models import Severity


@pytest.mark.parametrize("severity", list(Severity))
def test_severity_badge_renders_closed_enum_as_plain_text(severity: Severity) -> None:
    """Every supported severity renders deterministic plain text and its configured style."""

    QApplication.instance() or QApplication([])
    badge = SeverityBadge(severity)

    assert badge.text() == severity.value.upper()
    assert badge.textFormat() is Qt.TextFormat.PlainText
    assert badge.alignment() == Qt.AlignmentFlag.AlignCenter
    assert SeverityBadge._STYLES[severity] in badge.styleSheet()
    assert "font-weight:600" in badge.styleSheet()
    assert badge.minimumWidth() == 72


def test_severity_badge_rejects_unvalidated_values() -> None:
    """Finding-controlled strings cannot bypass the closed Severity enum."""

    QApplication.instance() or QApplication([])
    with pytest.raises(TypeError, match="severity must be a Severity"):
        SeverityBadge(cast(Severity, "critical"))

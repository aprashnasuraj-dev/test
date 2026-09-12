"""Coverage tests for the audit progress dialog."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from ens_audit.gui.widgets.progress_dialog import ProgressDialog


def _dialog() -> ProgressDialog:
    """Construct one offscreen progress dialog without starting an event loop."""

    QApplication.instance() or QApplication([])
    return ProgressDialog()


def test_progress_dialog_updates_and_clamps_pipeline_counters() -> None:
    """Normal, negative, oversized, and zero-total counters stay within 0..100."""

    dialog = _dialog()
    try:
        dialog.update_progress("manager", "sast", 2, 4)
        assert dialog.progress_bar.value() == 50
        assert dialog.status_label.text() == "manager — sast (2/4)"

        dialog.update_progress("portal", "deps", -3, 0)
        assert dialog.progress_bar.value() == 0
        assert dialog.status_label.text() == "portal — deps (0/1)"

        dialog.update_progress("workers", "report", 99, 3)
        assert dialog.progress_bar.value() == 100
        assert dialog.status_label.text() == "workers — report (3/3)"
    finally:
        dialog.close()


def test_progress_dialog_cancel_emits_once_per_request_and_updates_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cancellation remains cooperative: the dialog emits intent and changes only its label."""

    dialog = _dialog()
    emitted: list[bool] = []
    dialog.cancel_requested.connect(lambda: emitted.append(True))
    try:
        dialog._request_cancel()
        assert emitted == [True]
        assert dialog.status_label.text() == "Cancellation requested…"
    finally:
        dialog.close()

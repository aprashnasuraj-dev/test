"""Headless smoke tests for the PySide6 desktop interface."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from ens_audit.gui.main_window import MainWindow  # noqa: E402
from ens_audit.pipeline import orchestrator as orchestrator_module  # noqa: E402


def test_main_window_constructs_offscreen(
    monkeypatch: object,
    tmp_path: Path,
) -> None:
    """The complete seven-tab GUI must construct without network or scanner execution.

    Security invariant: the smoke test redirects persistence to a temporary path and never
    starts an audit worker.
    """

    monkeypatch.setattr(  # type: ignore[attr-defined]
        orchestrator_module,
        "DATABASE_PATH",
        tmp_path / "audit.sqlite3",
    )
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    try:
        assert window.tabs.count() == 7
        assert window.tabs.tabText(0) == "Dashboard"
        assert window.tabs.tabText(2) == "Findings"
        assert window.tabs.tabText(3) == "Known Issues"
        assert window.tabs.tabText(4) == "Report"
        assert window.orchestrator.current_run_id is None
        assert app.applicationName()
    finally:
        window.close()

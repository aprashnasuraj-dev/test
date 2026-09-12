"""Executable entry point for ENS Audit Runner."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ens_audit.config import APP_NAME, ensure_runtime_directories
from ens_audit.gui.main_window import MainWindow


def main() -> int:
    """Start the Windows-native PySide6 audit runner.

    Security invariant: application startup creates only fixed runner-owned directories before
    constructing the GUI; no audit target or subprocess is launched implicitly.
    """

    ensure_runtime_directories()
    app = QApplication.instance()
    owns_app = app is None
    if app is None:
        app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = MainWindow()
    window.show()
    if not owns_app:
        return 0
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

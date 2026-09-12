"""Executable entry point for ENS Audit Runner."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from ens_audit.config import APP_NAME, ensure_runtime_directories
from ens_audit.gui.main_window import MainWindow

_SMOKE_TEST_MARKER = "SMOKE_TEST_OK"
_SMOKE_TEST_DURATION_MS = 2_000


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line options without executing audit work."""

    parser = argparse.ArgumentParser(prog="ENSAuditRunner")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Construct the GUI, run the Qt event loop for two seconds, write a startup marker, and exit.",
    )
    return parser.parse_args(argv)


def _smoke_log_path() -> Path:
    """Return the fixed per-user Windows smoke-test log path.

    Security invariant: smoke mode writes only below ``LOCALAPPDATA`` using fixed runner-owned
    path components; no command-line value influences the destination.
    """

    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        raise RuntimeError("LOCALAPPDATA is required for --smoke-test")
    return Path(local_app_data) / "ens-audit" / "logs" / "startup.log"


def _write_smoke_success() -> Path:
    """Write the deterministic smoke-test success marker and return its path."""

    path = _smoke_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{_SMOKE_TEST_MARKER}\n", encoding="utf-8")
    return path


def main(argv: Sequence[str] | None = None) -> int:
    """Start the Windows-native PySide6 audit runner or its bounded smoke test.

    Security invariant: application startup creates only fixed runner-owned directories before
    constructing the GUI; no audit target or subprocess is launched implicitly.
    """

    args = parse_args(argv)
    ensure_runtime_directories()
    app = QApplication.instance()
    owns_app = app is None
    if app is None:
        app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = MainWindow()
    window.show()

    if args.smoke_test:
        QTimer.singleShot(_SMOKE_TEST_DURATION_MS, app.quit)
        exit_code = app.exec()
        window.close()
        if exit_code == 0:
            _write_smoke_success()
        return exit_code

    if not owns_app:
        return 0
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

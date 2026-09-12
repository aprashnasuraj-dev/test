"""Read-only, path-contained source preview widget."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QPlainTextEdit, QWidget

from ens_audit.models import Location

_MAX_PREVIEW_BYTES = 512 * 1024
_CONTEXT_LINES = 10


class CodePreview(QPlainTextEdit):
    """Display bounded source context for a normalized finding location.

    Security invariant: only regular files resolving inside the supplied audited root are
    readable, and content is rendered as plain text rather than HTML.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a read-only monospace preview surface.

        Security invariant: users cannot edit source through this widget.
        """

        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.setPlaceholderText("Select a finding to preview source context.")

    def show_location(self, repo_root: Path, location: Location) -> None:
        """Render source lines surrounding ``location`` within ``repo_root``.

        Security invariant: canonical path containment and a file-size cap are enforced before
        any source bytes are read.
        """

        root = repo_root.resolve()
        candidate = (root / location.file).resolve()
        if not candidate.is_relative_to(root):
            self.setPlainText("Preview blocked: source path escapes the audited repository.")
            return
        if not candidate.is_file() or candidate.is_symlink():
            self.setPlainText("Preview unavailable: source file is missing or not a regular file.")
            return
        if candidate.stat().st_size > _MAX_PREVIEW_BYTES:
            self.setPlainText("Preview unavailable: source file exceeds the preview size limit.")
            return

        lines = candidate.read_text(encoding="utf-8", errors="replace").splitlines()
        target = max(1, location.line or 1)
        start = max(1, target - _CONTEXT_LINES)
        end = min(len(lines), target + _CONTEXT_LINES)
        rendered = [
            f"{number:>6} │ {lines[number - 1]}" for number in range(start, end + 1)
        ]
        self.setPlainText("\n".join(rendered))

        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        for _ in range(max(0, target - start)):
            cursor.movePosition(cursor.MoveOperation.Down)
        self.setTextCursor(cursor)
        self.centerCursor()

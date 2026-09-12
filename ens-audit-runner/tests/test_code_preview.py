"""Coverage tests for the source preview widget."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from ens_audit.gui.widgets.code_preview import CodePreview
from ens_audit.models import Location


def _preview() -> CodePreview:
    QApplication.instance() or QApplication([])
    return CodePreview()


def test_code_preview_renders_source_context(tmp_path: Path) -> None:
    source = tmp_path / "src" / "flow.ts"
    source.parent.mkdir()
    source.write_text("\n".join(f"line {number}" for number in range(1, 31)), encoding="utf-8")
    preview = _preview()
    try:
        preview.show_location(tmp_path, Location("src/flow.ts", line=15))
        rendered = preview.toPlainText()
        assert "     5 │ line 5" in rendered
        assert "    15 │ line 15" in rendered
        assert "    25 │ line 25" in rendered
        assert preview.isReadOnly()
    finally:
        preview.close()


def test_code_preview_rejects_missing_and_oversized_files(tmp_path: Path) -> None:
    preview = _preview()
    try:
        preview.show_location(tmp_path, Location("missing.ts", line=1))
        assert "missing or not a regular file" in preview.toPlainText()

        oversized = tmp_path / "large.ts"
        oversized.write_bytes(b"x" * (512 * 1024 + 1))
        preview.show_location(tmp_path, Location("large.ts", line=1))
        assert "exceeds the preview size limit" in preview.toPlainText()
    finally:
        preview.close()

"""Report preview, export, and clipboard controls."""

from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ens_audit.models import AuditReport, Finding, FindingStatus
from ens_audit.pipeline.stage_report import ReportStage

_MAX_PREVIEW_BYTES = 2 * 1024 * 1024


class ReportView(QWidget):
    """Preview and export generated audit artifacts.

    Security invariant: report content is displayed and copied as plain text; export copies only
    runner-generated files from the recorded report directory.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build report preview, export buttons, and finding selector.

        Security invariant: no report content is interpreted as HTML or executable code.
        """

        super().__init__(parent)
        self._report: AuditReport | None = None
        self._finding_by_label: dict[str, Finding] = {}

        self.preview = QPlainTextEdit(self)
        self.preview.setReadOnly(True)
        self.preview.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.preview.setPlaceholderText("Run an audit to generate audit-report.md")

        self.finding_selector = QComboBox(self)
        self.finding_selector.setMinimumWidth(360)
        copy_button = QPushButton("Copy Finding", self)
        copy_button.clicked.connect(self.copy_selected_finding)

        export_json = QPushButton("Export JSON", self)
        export_markdown = QPushButton("Export Markdown", self)
        export_immunefi = QPushButton("Export Immunefi Findings", self)
        export_json.clicked.connect(lambda: self._export_file("findings.json", "JSON (*.json)"))
        export_markdown.clicked.connect(
            lambda: self._export_file("audit-report.md", "Markdown (*.md)")
        )
        export_immunefi.clicked.connect(self.export_immunefi_directory)

        selector_row = QHBoxLayout()
        selector_row.addWidget(QLabel("Finding", self))
        selector_row.addWidget(self.finding_selector, 1)
        selector_row.addWidget(copy_button)

        actions = QHBoxLayout()
        actions.addWidget(export_json)
        actions.addWidget(export_markdown)
        actions.addWidget(export_immunefi)
        actions.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addLayout(selector_row)
        layout.addWidget(self.preview, 1)
        layout.addLayout(actions)

    def set_report(self, report: AuditReport) -> None:
        """Load one generated report into the preview and finding selector.

        Security invariant: only files contained by ``report.output_dir`` are read and previews
        are capped before loading into the GUI.
        """

        self._report = report
        markdown = self._contained_file("audit-report.md")
        if markdown is not None and markdown.stat().st_size <= _MAX_PREVIEW_BYTES:
            self.preview.setPlainText(markdown.read_text(encoding="utf-8", errors="replace"))
        else:
            self.preview.setPlainText("Report preview unavailable or exceeds the preview limit.")

        self.finding_selector.clear()
        self._finding_by_label.clear()
        for index, finding in enumerate(report.findings, start=1):
            if finding.status is not FindingStatus.OPEN:
                continue
            label = f"{index:03d} | {finding.severity.value} | {finding.asset} | {finding.title}"
            self._finding_by_label[label] = finding
            self.finding_selector.addItem(label)

    def copy_selected_finding(self) -> None:
        """Copy one open finding in Immunefi layout to the system clipboard.

        Security invariant: clipboard text is generated from normalized finding fields and is
        not executed by this application.
        """

        finding = self._finding_by_label.get(self.finding_selector.currentText())
        if finding is None:
            return
        QGuiApplication.clipboard().setText(ReportStage._immunefi_markdown(finding))

    def export_immunefi_directory(self) -> None:
        """Copy generated individual finding Markdown files to a user-selected directory.

        Security invariant: source traversal is restricted to the runner-generated findings
        directory and symlinks are not followed.
        """

        source = self._contained_file("findings", require_file=False)
        if source is None or not source.is_dir() or source.is_symlink():
            return
        destination = QFileDialog.getExistingDirectory(self, "Export Immunefi Findings")
        if not destination:
            return
        destination_root = Path(destination) / "findings"
        destination_root.mkdir(parents=True, exist_ok=True)
        for path in source.glob("*.md"):
            if path.is_file() and not path.is_symlink():
                shutil.copy2(path, destination_root / path.name)
        QMessageBox.information(self, "Export Complete", f"Exported to {destination_root}")

    def _export_file(self, name: str, file_filter: str) -> None:
        """Copy one known generated report file to a user-selected destination.

        Security invariant: ``name`` is resolved beneath the recorded report output directory
        before copying.
        """

        source = self._contained_file(name)
        if source is None:
            return
        destination, _ = QFileDialog.getSaveFileName(self, f"Export {name}", name, file_filter)
        if not destination:
            return
        shutil.copy2(source, Path(destination))

    def _contained_file(self, name: str, *, require_file: bool = True) -> Path | None:
        """Resolve a generated artifact under the current report directory.

        Security invariant: path canonicalization prevents export helpers from reading outside
        ``AuditReport.output_dir``.
        """

        if self._report is None:
            return None
        root = self._report.output_dir.resolve()
        candidate = (root / name).resolve()
        if not candidate.is_relative_to(root):
            return None
        if require_file and (not candidate.is_file() or candidate.is_symlink()):
            return None
        return candidate

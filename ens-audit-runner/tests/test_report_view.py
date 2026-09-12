"""Coverage tests for report preview and export behavior."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from ens_audit.gui.report_view import ReportView
from ens_audit.models import AuditReport, Finding, FindingStatus, Location, Severity


def _app() -> QApplication:
    app = QApplication.instance()
    return app if app is not None else QApplication([])


def _finding(*, status: FindingStatus = FindingStatus.OPEN) -> Finding:
    return Finding(
        title="Unsafe redirect",
        severity=Severity.HIGH,
        asset="manager",
        stage="sast",
        rule_id="test-rule",
        root_cause="untrusted_redirect",
        location=Location("src/page.ts", 12),
        description="Untrusted destination reaches navigation.",
        evidence="window.open(target)",
        status=status,
        suppressed_by="KNOWN-1" if status is FindingStatus.SUPPRESSED else None,
    )


def _report(tmp_path: Path, findings: tuple[Finding, ...]) -> AuditReport:
    return AuditReport("a" * 40, findings, ("sast",), tmp_path)


def test_report_view_previews_markdown_and_lists_only_open_findings(tmp_path: Path) -> None:
    _app()
    (tmp_path / "audit-report.md").write_text("# Audit report\n", encoding="utf-8")
    view = ReportView()
    try:
        view.set_report(_report(tmp_path, (_finding(), _finding(status=FindingStatus.SUPPRESSED))))
        assert view.preview.toPlainText() == "# Audit report\n"
        assert view.finding_selector.count() == 1
        assert "High | manager | Unsafe redirect" in view.finding_selector.currentText()

        view.copy_selected_finding()
        assert "Unsafe redirect" in QGuiApplication.clipboard().text()
    finally:
        view.close()


def test_report_view_handles_missing_preview_and_empty_copy(tmp_path: Path) -> None:
    _app()
    view = ReportView()
    try:
        view.set_report(_report(tmp_path, ()))
        assert "preview unavailable" in view.preview.toPlainText().lower()
        view.copy_selected_finding()
        assert view.finding_selector.count() == 0
    finally:
        view.close()


def test_report_view_exports_single_file_and_immunefi_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _app()
    (tmp_path / "audit-report.json").write_text('{"ok": true}\n', encoding="utf-8")
    findings_dir = tmp_path / "findings"
    findings_dir.mkdir()
    (findings_dir / "one.md").write_text("finding one\n", encoding="utf-8")
    destination = tmp_path / "exports"
    destination.mkdir()
    json_destination = destination / "copy.json"

    monkeypatch.setattr(
        "ens_audit.gui.report_view.QFileDialog.getSaveFileName",
        lambda *_args, **_kwargs: (str(json_destination), "JSON (*.json)"),
    )
    monkeypatch.setattr(
        "ens_audit.gui.report_view.QFileDialog.getExistingDirectory",
        lambda *_args, **_kwargs: str(destination),
    )
    messages: list[str] = []
    monkeypatch.setattr(
        "ens_audit.gui.report_view.QMessageBox.information",
        lambda _parent, _title, text: messages.append(text),
    )

    view = ReportView()
    try:
        view.set_report(_report(tmp_path, (_finding(),)))
        view._export_file("audit-report.json", "JSON (*.json)")
        assert json_destination.read_text(encoding="utf-8") == '{"ok": true}\n'

        view.export_immunefi_directory()
        assert (destination / "findings" / "one.md").read_text(encoding="utf-8") == "finding one\n"
        assert messages and "Exported to" in messages[0]
    finally:
        view.close()

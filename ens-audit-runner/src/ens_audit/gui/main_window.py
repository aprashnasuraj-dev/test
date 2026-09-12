"""Top-level PySide6 window wiring the audit pipeline to GUI views."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ens_audit.config import ASSETS, REPOS_DIR
from ens_audit.gui.dashboard import Dashboard
from ens_audit.gui.findings_view import FindingsView
from ens_audit.gui.known_issues_view import KnownIssuesView
from ens_audit.gui.pipeline_view import PipelineView
from ens_audit.gui.report_view import ReportView
from ens_audit.gui.settings_view import SettingsView
from ens_audit.gui.widgets.progress_dialog import ProgressDialog
from ens_audit.models import AuditReport
from ens_audit.pipeline.orchestrator import PipelineCancelled, PipelineOrchestrator
from ens_audit.tooling import DEFAULT_TOOL_RUNNER


class StageSelectionDialog(QDialog):
    """Collect a validated subset of configured analysis stages.

    Security invariant: users can select only the closed stage vocabulary exposed by the
    orchestrator; free-form stage names are never accepted.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build one checkbox per configured analysis stage."""

        super().__init__(parent)
        self.setWindowTitle("Select Audit Stages")
        self._checks: dict[str, QCheckBox] = {}
        layout = QVBoxLayout(self)
        prompt = QLabel(
            "Choose analysis stages. Known-issue filtering and reporting run automatically."
        )
        layout.addWidget(prompt)
        for stage in PipelineOrchestrator.ANALYSIS_STAGES:
            checkbox = QCheckBox(stage.replace("_", " ").title(), self)
            checkbox.setChecked(True)
            self._checks[stage] = checkbox
            layout.addWidget(checkbox)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_stages(self) -> list[str]:
        """Return checked stage identifiers in canonical order."""

        return [stage for stage, checkbox in self._checks.items() if checkbox.isChecked()]


class AuditWorker(QObject):
    """Run async audit orchestration inside a dedicated QThread."""

    progress = Signal(str, str, int, int)
    log = Signal(str)
    report_ready = Signal(object)
    failed = Signal(str)
    cancelled = Signal()
    finished = Signal()

    def __init__(
        self,
        orchestrator: PipelineOrchestrator,
        mode: str,
        selected_stages: list[str] | None = None,
    ) -> None:
        """Configure one worker run mode and optional validated stage list."""

        super().__init__()
        if mode not in {"full", "selected", "retry"}:
            raise ValueError("unsupported worker mode")
        self.orchestrator = orchestrator
        self.mode = mode
        self.selected_stages = selected_stages or []

    @Slot()
    def run(self) -> None:
        """Execute the selected orchestrator entry point and emit terminal state."""

        self.orchestrator.progress = self.progress.emit
        self.orchestrator.logger = self.log.emit
        try:
            if self.mode == "full":
                report = asyncio.run(self.orchestrator.run_full_audit())
            elif self.mode == "selected":
                report = asyncio.run(self.orchestrator.run_selected(self.selected_stages))
            else:
                report = asyncio.run(self.orchestrator.retry_failed())
        except PipelineCancelled:
            self.cancelled.emit()
        except Exception as exc:  # noqa: BLE001 -- worker boundary converts failures to Qt signals.
            self.failed.emit(f"{type(exc).__name__}: {exc}"[:4000])
        else:
            self.report_ready.emit(report)
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    """Primary ENS Audit Runner desktop window."""

    def __init__(self) -> None:
        """Construct tabs, worker state, menus, and cross-view signal wiring."""

        super().__init__()
        self.setWindowTitle("ENS Audit Runner")
        self.resize(1320, 860)
        self.orchestrator = PipelineOrchestrator()
        self._thread: QThread | None = None
        self._worker: AuditWorker | None = None
        self._progress_dialog: ProgressDialog | None = None
        self._last_pair: tuple[str, str] | None = None
        self._stage_status: dict[tuple[str, str], str] = {}
        self._completed_assets: dict[str, set[str]] = {
            stage: set() for stage in PipelineOrchestrator.STAGES
        }

        self.dashboard = Dashboard(self)
        self.pipeline_view = PipelineView(self)
        self.findings_view = FindingsView(self)
        self.known_issues_view = KnownIssuesView(self)
        self.report_view = ReportView(self)
        self.settings_view = SettingsView(self)
        self.logs_tab = self._build_logs_tab()

        self.tabs = QTabWidget(self)
        self.tabs.addTab(self.dashboard, "Dashboard")
        self.tabs.addTab(self.pipeline_view, "Pipeline")
        self.tabs.addTab(self.findings_view, "Findings")
        self.tabs.addTab(self.known_issues_view, "Known Issues")
        self.tabs.addTab(self.report_view, "Report")
        self.tabs.addTab(self.settings_view, "Settings")
        self.tabs.addTab(self.logs_tab, "Logs")
        self.setCentralWidget(self.tabs)

        self.dashboard.run_full_requested.connect(self.run_full_audit)
        self.dashboard.run_selected_requested.connect(self.run_selected_stages)
        self.dashboard.export_requested.connect(self._show_report_tab)
        self.pipeline_view.pause_requested.connect(self.pause_audit)
        self.pipeline_view.resume_requested.connect(self.resume_audit)
        self.pipeline_view.retry_failed_requested.connect(self.retry_failed)
        self._build_menu()

    def _build_menu(self) -> None:
        """Create Settings and About actions."""

        settings_action = self.menuBar().addAction("Settings")
        settings_action.triggered.connect(lambda: self.tabs.setCurrentWidget(self.settings_view))
        about_action = self.menuBar().addAction("About")
        about_action.triggered.connect(self._show_about)

    def _build_logs_tab(self) -> QWidget:
        """Build timestamped log search/filter/export controls."""

        container = QWidget(self)
        self.log_view = QPlainTextEdit(container)
        self.log_view.setReadOnly(True)
        self.log_view.document().setMaximumBlockCount(20000)
        self.log_search = QLineEdit(container)
        self.log_search.setPlaceholderText("Search logs")
        find_next = QPushButton("Find Next", container)
        export = QPushButton("Export Log", container)
        find_next.clicked.connect(self._find_next_log)
        export.clicked.connect(self._export_log)
        row = QHBoxLayout()
        row.addWidget(self.log_search, 1)
        row.addWidget(find_next)
        row.addWidget(export)
        layout = QVBoxLayout(container)
        layout.addLayout(row)
        layout.addWidget(self.log_view, 1)
        return container

    @Slot()
    def run_full_audit(self) -> None:
        """Start a complete seven-stage audit in a worker thread."""

        self._start_worker("full")

    @Slot()
    def run_selected_stages(self) -> None:
        """Prompt for a closed subset of stages and start them in a worker thread."""

        if self._thread is not None:
            self._busy_message()
            return
        dialog = StageSelectionDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        stages = dialog.selected_stages()
        if not stages:
            QMessageBox.warning(self, "No Stages Selected", "Select at least one analysis stage.")
            return
        self._start_worker("selected", stages)

    @Slot()
    def retry_failed(self) -> None:
        """Retry incomplete stages from the orchestrator's current run."""

        if self.orchestrator.current_run_id is None:
            QMessageBox.information(self, "Nothing to Retry", "Run an audit first.")
            return
        self._start_worker("retry")

    @Slot()
    def pause_audit(self) -> None:
        """Pause execution at the next cooperative stage boundary."""

        self.orchestrator.control.pause()
        self._append_log("pause requested; current scanner will finish before pausing")

    @Slot()
    def resume_audit(self) -> None:
        """Release a cooperative pipeline pause."""

        self.orchestrator.control.resume()
        self._append_log("resume requested")

    def _start_worker(self, mode: str, stages: list[str] | None = None) -> None:
        """Create and start one QThread audit worker with session-only tool settings."""

        if self._thread is not None:
            self._busy_message()
            return

        settings = self.settings_view.session_settings()
        DEFAULT_TOOL_RUNNER.set_session_environment(
            {
                "SEMGREP_APP_TOKEN": settings.semgrep_app_token,
                "SNYK_TOKEN": settings.snyk_token,
            }
        )
        DEFAULT_TOOL_RUNNER.set_disabled_tools(
            () if settings.codeql_terms_accepted else ("codeql",)
        )
        if not settings.codeql_terms_accepted:
            codeql_installed = bool(
                DEFAULT_TOOL_RUNNER.native_path("codeql")
                or DEFAULT_TOOL_RUNNER.wsl_path("codeql")
            )
            if codeql_installed:
                self._append_log("CodeQL skipped for this run: usage terms not confirmed")

        self._last_pair = None
        self._stage_status.clear()
        self._completed_assets = {stage: set() for stage in PipelineOrchestrator.STAGES}
        self._progress_dialog = ProgressDialog(self)
        self._progress_dialog.cancel_requested.connect(self.orchestrator.control.cancel)
        self._progress_dialog.show()

        thread = QThread(self)
        worker = AuditWorker(self.orchestrator, mode, stages)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self._on_progress)
        worker.log.connect(self._append_log)
        worker.report_ready.connect(self._on_report)
        worker.failed.connect(self._on_failed)
        worker.cancelled.connect(self._on_cancelled)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._worker_finished)
        self._thread = thread
        self._worker = worker
        thread.start()

    @Slot(str, str, int, int)
    def _on_progress(self, asset: str, stage: str, current: int, total: int) -> None:
        """Update pipeline/dashboard progress from worker metadata."""

        self._finalize_previous_pair()
        if self._progress_dialog is not None:
            self._progress_dialog.update_progress(asset, stage, current, total)
        if asset != "all" and (asset, stage) in self.pipeline_view._row_by_key:
            self._last_pair = (asset, stage)
            self._stage_status[(asset, stage)] = "running"
            self.pipeline_view.set_stage_status(asset, stage, "running", 0)

    @Slot(str)
    def _append_log(self, message: str) -> None:
        """Append one bounded plain-text worker log line to both log surfaces."""

        cleaned = "".join(
            character for character in message if character >= " " or character == "\t"
        )[:4000]
        self.pipeline_view.append_log(cleaned)
        self.log_view.appendPlainText(cleaned)
        complete = re.match(r"complete ([^:]+):([^;]+);", cleaned)
        failed = re.match(r"failed ([^:]+):([^;]+);", cleaned)
        skipped = re.match(r"skip ([^:]+):([^;]+);", cleaned)
        if complete:
            self._set_terminal_stage(complete.group(1), complete.group(2), "complete")
        elif failed:
            self._set_terminal_stage(failed.group(1), failed.group(2), "failed")
        elif skipped:
            self._set_terminal_stage(skipped.group(1), skipped.group(2), "skipped")

    @Slot(object)
    def _on_report(self, report_object: object) -> None:
        """Propagate a completed AuditReport to dashboard, findings, and report views."""

        if not isinstance(report_object, AuditReport):
            self._on_failed("Worker returned an invalid report object")
            return
        self._finalize_previous_pair()
        report = report_object
        repo_root = (REPOS_DIR / "audit-comp-ens").resolve()
        repo_roots = {spec.name: (repo_root / spec.relative_path).resolve() for spec in ASSETS}
        findings = list(report.findings)
        self.dashboard.set_asset_count(len(ASSETS))
        self.dashboard.set_findings(findings)
        self.findings_view.set_findings(findings, repo_roots)
        self.report_view.set_report(report)
        self.tabs.setCurrentWidget(self.findings_view)
        self._append_log(f"report generated at {report.output_dir}")

    @Slot(str)
    def _on_failed(self, message: str) -> None:
        """Display a bounded pipeline failure message and preserve logs for review."""

        self._append_log(f"audit failed: {message[:4000]}")
        QMessageBox.critical(self, "Audit Failed", message[:2000])

    @Slot()
    def _on_cancelled(self) -> None:
        """Record cooperative cancellation without treating it as a scanner failure."""

        self._append_log("audit cancelled at a stage boundary")
        QMessageBox.information(self, "Audit Cancelled", "The audit stopped at a stage boundary.")

    @Slot()
    def _worker_finished(self) -> None:
        """Release worker references and scrub session-only scanner credentials."""

        if self._progress_dialog is not None:
            self._progress_dialog.close()
            self._progress_dialog.deleteLater()
        DEFAULT_TOOL_RUNNER.set_session_environment({})
        DEFAULT_TOOL_RUNNER.set_disabled_tools(())
        self._progress_dialog = None
        self._worker = None
        self._thread = None

    def _set_terminal_stage(self, asset: str, stage: str, status: str) -> None:
        """Record a completed/failed/skipped stage and update aggregate progress."""

        pair = (asset, stage)
        if pair not in self.pipeline_view._row_by_key:
            return
        self._stage_status[pair] = status
        percent = 100 if status in {"complete", "skipped"} else 0
        self.pipeline_view.set_stage_status(asset, stage, status, percent)
        if status in {"complete", "skipped"}:
            self._completed_assets.setdefault(stage, set()).add(asset)
            self.dashboard.set_stage_progress(stage, len(self._completed_assets[stage]))

    def _finalize_previous_pair(self) -> None:
        """Mark an unfailed prior progress row complete when the next boundary is reached."""

        if self._last_pair is None:
            return
        status = self._stage_status.get(self._last_pair)
        if status == "running":
            self._set_terminal_stage(self._last_pair[0], self._last_pair[1], "complete")
        self._last_pair = None

    def _show_report_tab(self) -> None:
        """Navigate to the report tab without mutating report state."""

        self.tabs.setCurrentWidget(self.report_view)

    def _show_about(self) -> None:
        """Display static application purpose and scope information."""

        QMessageBox.about(
            self,
            "About ENS Audit Runner",
            "ENS Audit Runner performs source-only security analysis against the configured "
            "pinned ENS audit scope.",
        )

    def _find_next_log(self) -> None:
        """Find the next plain-text log occurrence from the search field."""

        query = self.log_search.text()
        if query:
            self.log_view.find(query)

    def _export_log(self) -> None:
        """Export displayed logs to a user-selected UTF-8 text file."""

        destination, _ = QFileDialog.getSaveFileName(
            self,
            "Export Log",
            "ens-audit.log",
            "Log (*.log);;Text (*.txt)",
        )
        if destination:
            Path(destination).write_text(self.log_view.toPlainText(), encoding="utf-8")

    def _busy_message(self) -> None:
        """Inform the user that concurrent audit workers are not permitted."""

        QMessageBox.information(self, "Audit Running", "An audit is already running.")

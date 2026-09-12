"""Settings tab for audit source identity, tool discovery, and session credentials."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHeaderView,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ens_audit.config import (
    ACTIVE_UPSTREAM_COMMIT,
    REQUIRED_TOOLS,
    UPSTREAM_BRANCH,
    UPSTREAM_REPOSITORY,
)
from ens_audit.tooling import DEFAULT_TOOL_RUNNER


@dataclass(frozen=True, slots=True)
class SessionSettings:
    """Represent non-persisted scanner settings entered in the GUI.

    Security invariant: credential values live only in process memory and are never written by
    this view to QSettings, logs, or disk.
    """

    semgrep_app_token: str
    snyk_token: str
    codeql_terms_accepted: bool


class SettingsView(QWidget):
    """Display immutable scope settings and discover executable analyzer routes.

    Security invariant: entering settings never executes an analyzer or persists credential
    text. WSL discovery invokes only ``which <tool>`` through the shared argv-only resolver.
    """

    settings_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build scope, credential, and tool-discovery controls."""

        super().__init__(parent)

        self.repository = QLineEdit(UPSTREAM_REPOSITORY, self)
        self.branch = QLineEdit(UPSTREAM_BRANCH, self)
        self.commit = QLineEdit(ACTIVE_UPSTREAM_COMMIT, self)
        for field in (self.repository, self.branch, self.commit):
            field.setReadOnly(True)

        scope_box = QGroupBox("Pinned Audit Source", self)
        scope_form = QFormLayout(scope_box)
        scope_form.addRow("Repository", self.repository)
        scope_form.addRow("Branch", self.branch)
        scope_form.addRow("Commit", self.commit)

        self.codeql_terms = QCheckBox("I confirm CodeQL usage terms are accepted", self)
        self.semgrep_token = QLineEdit(self)
        self.semgrep_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.semgrep_token.setPlaceholderText("Optional SEMGREP_APP_TOKEN for this session")
        self.snyk_token = QLineEdit(self)
        self.snyk_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.snyk_token.setPlaceholderText("Optional SNYK_TOKEN for this session")
        for widget in (self.codeql_terms, self.semgrep_token, self.snyk_token):
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self.settings_changed.emit)
            else:
                widget.toggled.connect(self.settings_changed.emit)

        credential_box = QGroupBox("Session Credentials", self)
        credential_form = QFormLayout(credential_box)
        credential_form.addRow(self.codeql_terms)
        credential_form.addRow("Semgrep API key", self.semgrep_token)
        credential_form.addRow("Snyk token", self.snyk_token)

        self.tool_table = QTableWidget(0, 4, self)
        self.tool_table.setHorizontalHeaderLabels(("Tool", "Native path", "WSL path", "Active route"))
        self.tool_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tool_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        detect = QPushButton("Detect Tools", self)
        detect.clicked.connect(self.detect_tools)

        layout = QVBoxLayout(self)
        layout.addWidget(scope_box)
        layout.addWidget(credential_box)
        layout.addWidget(self.tool_table, 1)
        layout.addWidget(detect)
        self.detect_tools()

    def detect_tools(self) -> None:
        """Refresh actual native/WSL resolution for every configured tool."""

        DEFAULT_TOOL_RUNNER.clear_cache()
        self.tool_table.setRowCount(0)
        for tool in REQUIRED_TOOLS:
            native = DEFAULT_TOOL_RUNNER.native_path(tool)
            if native:
                wsl_path = "Not checked (native preferred)"
                route = "Native"
            else:
                discovered_wsl = DEFAULT_TOOL_RUNNER.wsl_path(tool)
                wsl_path = discovered_wsl or "Not found"
                route = "WSL" if discovered_wsl else "Missing"

            row = self.tool_table.rowCount()
            self.tool_table.insertRow(row)
            values = (tool, native or "Not found", wsl_path, route)
            for column, value in enumerate(values):
                self.tool_table.setItem(row, column, QTableWidgetItem(value))

    def session_settings(self) -> SessionSettings:
        """Return current in-memory credential/settings values.

        Security invariant: returned secrets are never logged or persisted by this method.
        """

        return SessionSettings(
            semgrep_app_token=self.semgrep_token.text(),
            snyk_token=self.snyk_token.text(),
            codeql_terms_accepted=self.codeql_terms.isChecked(),
        )

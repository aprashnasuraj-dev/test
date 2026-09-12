"""Regression tests for safe native/WSL analyzer execution."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from ens_audit import tooling


def test_windows_path_to_wsl_converts_drive_path() -> None:
    """Absolute Windows paths must map to the corresponding WSL mount."""

    assert tooling.windows_path_to_wsl(r"C:\Users\alice\ens") == "/mnt/c/Users/alice/ens"


def test_convert_argument_for_wsl_handles_file_uri_and_assignment() -> None:
    """Common argv path shapes must be converted without shell parsing."""

    assert (
        tooling.convert_argument_for_wsl("file:///D:/audit/repo")
        == "file:///mnt/d/audit/repo"
    )
    assert (
        tooling.convert_argument_for_wsl(r"--output=C:\audit\result.json")
        == "--output=/mnt/c/audit/result.json"
    )


def test_resolve_prefers_native_binary(monkeypatch: pytest.MonkeyPatch) -> None:
    """A native executable must win over WSL fallback."""

    runner = tooling.ToolRunner()

    def fake_which(name: str) -> str | None:
        if name == "semgrep":
            return r"C:\Tools\semgrep.exe"
        if name in {"wsl", "wsl.exe"}:
            return r"C:\Windows\System32\wsl.exe"
        return None

    run = Mock()
    monkeypatch.setattr(tooling.shutil, "which", fake_which)
    monkeypatch.setattr(tooling.subprocess, "run", run)

    resolved = runner.resolve("semgrep")
    assert resolved is not None
    assert resolved.mode == "native"
    assert resolved.executable == r"C:\Tools\semgrep.exe"
    run.assert_not_called()


def test_wsl_run_uses_argv_and_forwards_secret_by_environment(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """WSL execution must avoid shell strings and keep secret values out of argv."""

    runner = tooling.ToolRunner()
    secret = "session-token-value"
    runner.set_session_environment({"SNYK_TOKEN": secret})

    def fake_which(name: str) -> str | None:
        if name in {"wsl", "wsl.exe"}:
            return r"C:\Windows\System32\wsl.exe"
        return None

    probe = subprocess.CompletedProcess(
        ["wsl.exe", "-e", "which", "snyk"],
        0,
        stdout="/usr/local/bin/snyk\n",
        stderr="",
    )
    executed = subprocess.CompletedProcess(["snyk"], 0, stdout="{}", stderr="")
    run = Mock(side_effect=[probe, executed])
    monkeypatch.setattr(tooling.shutil, "which", fake_which)
    monkeypatch.setattr(tooling.subprocess, "run", run)

    result = runner.run("snyk", ["test", "--json"], cwd=tmp_path, timeout_s=30)

    assert result.returncode == 0
    execution = run.call_args_list[1]
    argv = execution.args[0]
    assert argv[:2] == [r"C:\Windows\System32\wsl.exe", "--cd"]
    assert argv[-3:] == ["snyk", "test", "--json"]
    assert "-e" in argv
    assert secret not in argv
    assert execution.kwargs["shell"] is False
    assert execution.kwargs["env"]["SNYK_TOKEN"] == secret
    assert "SNYK_TOKEN/u" in execution.kwargs["env"]["WSLENV"]


def test_disabled_tool_is_not_resolved(monkeypatch: pytest.MonkeyPatch) -> None:
    """Session policy must be able to disable an installed executable."""

    runner = tooling.ToolRunner()
    runner.set_disabled_tools(("codeql",))
    which = Mock(return_value=r"C:\Tools\codeql.exe")
    monkeypatch.setattr(tooling.shutil, "which", which)

    assert runner.resolve("codeql") is None
    which.assert_not_called()


def test_clear_cache_reprobes_wsl(monkeypatch: pytest.MonkeyPatch) -> None:
    """Detect Tools must be able to refresh a previously missing WSL executable."""

    runner = tooling.ToolRunner()
    monkeypatch.setattr(
        tooling.shutil,
        "which",
        lambda name: r"C:\Windows\System32\wsl.exe" if name in {"wsl", "wsl.exe"} else None,
    )
    first = subprocess.CompletedProcess(["wsl"], 1, stdout="", stderr="")
    second = subprocess.CompletedProcess(["wsl"], 0, stdout="/usr/bin/forge\n", stderr="")
    run = Mock(side_effect=[first, second])
    monkeypatch.setattr(tooling.subprocess, "run", run)

    assert runner.wsl_path("forge") is None
    assert runner.wsl_path("forge") is None
    assert run.call_count == 1

    runner.clear_cache()
    assert runner.wsl_path("forge") == "/usr/bin/forge"
    assert run.call_count == 2

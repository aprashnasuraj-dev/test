"""Tests for the executable entry point and bounded smoke-test mode."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from ens_audit.__main__ import _write_smoke_success, parse_args


def test_smoke_test_flag_parses_without_changing_default() -> None:
    """The opt-in smoke flag is explicit and normal startup remains the default."""

    assert parse_args(["--smoke-test"]).smoke_test is True
    assert parse_args([]).smoke_test is False


def test_smoke_success_marker_is_written_under_local_appdata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Smoke success is recorded only in the fixed per-user runner log location."""

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    path = _write_smoke_success()

    assert path == tmp_path / "ens-audit" / "logs" / "startup.log"
    assert path.read_text(encoding="utf-8") == "SMOKE_TEST_OK\n"


def test_smoke_log_requires_local_appdata(monkeypatch: pytest.MonkeyPatch) -> None:
    """Smoke mode fails closed when its fixed Windows user-data root is unavailable."""

    monkeypatch.delenv("LOCALAPPDATA", raising=False)

    with pytest.raises(RuntimeError, match="LOCALAPPDATA is required"):
        _write_smoke_success()

"""Tests for secret scanning without secret-value persistence."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from ens_audit.models import Asset, Severity
from ens_audit.pipeline.stage_secrets import SecretStage

_TRUFFLE_SECRET = "TRUFFLE_SECRET_MUST_NOT_PERSIST"
_DETECT_SECRET = "DETECT_SECRET_MUST_NOT_PERSIST"


def _asset(tmp_path: Path) -> Asset:
    """Build one local asset for secret-stage tests."""

    root = tmp_path / "asset"
    root.mkdir(exist_ok=True)
    return Asset("manager", root, "a" * 40)


def _trufflehog_line(*, verified: bool = True, filesystem: bool = False) -> str:
    """Return scanner JSON containing a raw value that normalization must discard."""

    source_kind = "Filesystem" if filesystem else "Git"
    return json.dumps(
        {
            "DetectorName": "TestToken",
            "Verified": verified,
            "Raw": _TRUFFLE_SECRET,
            "SourceMetadata": {
                "Data": {source_kind: {"file": "src/a.ts", "line": 12}}
            },
        }
    )


def _detect_secrets_json() -> str:
    """Return detect-secrets JSON containing a hash that must not become finding evidence."""

    return json.dumps(
        {
            "results": {
                "src/b.ts": [
                    {
                        "type": "High Entropy String",
                        "line_number": 8,
                        "hashed_secret": _DETECT_SECRET,
                    },
                    "ignored-non-mapping-record",
                ]
            }
        }
    )


def test_trufflehog_parser_discards_raw_secret(tmp_path: Path) -> None:
    """TruffleHog raw values never enter normalized findings or metadata."""

    findings, metadata = SecretStage._parse_trufflehog_text(
        "\n" + _trufflehog_line() + "\n", _asset(tmp_path)
    )
    assert findings[0].severity is Severity.HIGH
    assert findings[0].location.file == "src/a.ts"
    serialized = json.dumps([findings[0].to_dict(), *metadata])
    assert _TRUFFLE_SECRET not in serialized


def test_trufflehog_filesystem_metadata_is_normalized(tmp_path: Path) -> None:
    """Filesystem-mode scanner output retains only safe location metadata."""

    [finding], metadata = SecretStage._parse_trufflehog_text(
        _trufflehog_line(filesystem=True),
        _asset(tmp_path),
    )
    assert finding.location.file == "src/a.ts"
    assert finding.location.line == 12
    assert metadata[0]["file"] == "src/a.ts"


def test_trufflehog_unverified_is_medium(tmp_path: Path) -> None:
    """Unverified detector matches remain triage findings with reduced confidence."""

    [finding], _ = SecretStage._parse_trufflehog_text(
        _trufflehog_line(verified=False), _asset(tmp_path)
    )
    assert finding.severity is Severity.MEDIUM
    assert finding.confidence == 0.7


def test_detect_secrets_parser_discards_hash_and_handles_empty(tmp_path: Path) -> None:
    """detect-secrets output retains only structural metadata and empty output is harmless."""

    asset = _asset(tmp_path)
    assert SecretStage._parse_detect_secrets_text("", asset) == ([], [])
    findings, metadata = SecretStage._parse_detect_secrets_text(_detect_secrets_json(), asset)
    assert len(findings) == 1
    assert findings[0].location.line == 8
    serialized = json.dumps([findings[0].to_dict(), *metadata])
    assert _DETECT_SECRET not in serialized


def test_trufflehog_command_falls_back_to_filesystem(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A non-Git asset still receives a scoped filesystem scan."""

    asset = _asset(tmp_path)
    output_dir = tmp_path / "results"
    output_dir.mkdir()
    monkeypatch.setattr(
        "ens_audit.pipeline.stage_secrets.subprocess.run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            ["git"], 128, "", "not a repository"
        ),
    )

    argv, cwd, include_file = SecretStage._trufflehog_command(asset, output_dir)

    assert argv == ["trufflehog", "filesystem", str(asset.path), "--json"]
    assert cwd == asset.path
    assert include_file is None


def test_trufflehog_command_scopes_monorepo_history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Git history scanning uses the repository root and an asset include-path file."""

    asset_path = tmp_path / "apps" / "manager"
    asset_path.mkdir(parents=True)
    asset = Asset("manager", asset_path, "a" * 40)
    output_dir = tmp_path / "results"
    output_dir.mkdir()
    monkeypatch.setattr(
        "ens_audit.pipeline.stage_secrets.subprocess.run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            ["git"], 0, str(tmp_path) + "\n", ""
        ),
    )

    argv, cwd, include_file = SecretStage._trufflehog_command(asset, output_dir)

    assert argv[:3] == ["trufflehog", "git", tmp_path.as_uri()]
    assert cwd == tmp_path
    assert include_file is not None
    assert argv[-2:] == ["--include-paths", str(include_file)]
    assert include_file.read_text(encoding="utf-8") == r"^apps/manager(?:/.*)?$" + "\n"


def test_tool_rejects_nonzero_exit(tmp_path: Path) -> None:
    """Secret scanners fail closed when their process exits nonzero."""

    stage = SecretStage()

    class _Runner:
        def run(self, *_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(["scanner"], 2, "", "scanner failed")

    stage.tool_runner = _Runner()  # type: ignore[assignment]
    with pytest.raises(RuntimeError, match="scanner failed"):
        stage._tool(["scanner"], cwd=tmp_path, timeout_s=1)


@pytest.mark.asyncio
async def test_run_scans_both_tools_and_persists_only_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End-to-end stage orchestration sanitizes both scanner outputs before disk persistence."""

    monkeypatch.setattr(
        "ens_audit.pipeline.stage_secrets.RESULTS_DIR",
        tmp_path / "results",
    )
    monkeypatch.setattr(
        "ens_audit.pipeline.stage_secrets.subprocess.run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            ["git"], 128, "", "not a repository"
        ),
    )

    class _Runner:
        def available(self, _tool: str) -> bool:
            return True

        def run(
            self, tool: str, _args: object, **_kwargs: object
        ) -> subprocess.CompletedProcess[str]:
            stdout = (
                _trufflehog_line(filesystem=True)
                if tool == "trufflehog"
                else _detect_secrets_json()
            )
            return subprocess.CompletedProcess([tool], 0, stdout, "")

    stage = SecretStage()
    stage.tool_runner = _Runner()  # type: ignore[assignment]
    findings = await stage.run(_asset(tmp_path))
    assert len(findings) == 2
    sanitized = (tmp_path / "results/manager/secrets/secret-findings-sanitized.json").read_text()
    assert _TRUFFLE_SECRET not in sanitized
    assert _DETECT_SECRET not in sanitized
    assert "TestToken" in sanitized

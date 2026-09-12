"""Tests for pinned source acquisition."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from ens_audit.config import AssetSpec
from ens_audit.downloader import repo_downloader
from ens_audit.models import Asset


def test_run_git_uses_shell_false(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Git subprocesses must never enable shell interpretation."""

    completed = subprocess.CompletedProcess(["git"], 0, stdout="ok\n", stderr="")
    run = Mock(return_value=completed)
    monkeypatch.setattr(repo_downloader.shutil, "which", lambda _: "/usr/bin/git")
    monkeypatch.setattr(repo_downloader.subprocess, "run", run)

    assert repo_downloader._run_git(["status"], cwd=tmp_path) == "ok"
    kwargs = run.call_args.kwargs
    assert kwargs["shell"] is False
    assert kwargs["check"] is False
    assert kwargs["cwd"] == tmp_path
    assert kwargs["env"]["GIT_TERMINAL_PROMPT"] == "0"


def test_run_git_rejects_failed_command(monkeypatch: pytest.MonkeyPatch) -> None:
    """A nonzero Git exit code must fail closed."""

    completed = subprocess.CompletedProcess(["git"], 1, stdout="", stderr="bad revision")
    monkeypatch.setattr(repo_downloader.shutil, "which", lambda _: "/usr/bin/git")
    monkeypatch.setattr(repo_downloader.subprocess, "run", Mock(return_value=completed))

    with pytest.raises(repo_downloader.RepositoryDownloadError, match="bad revision"):
        repo_downloader._run_git(["checkout", "bad"])


def test_checkout_root_is_fixed_under_repos(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Checkout root must remain a direct child of the configured repository cache."""

    monkeypatch.setattr(repo_downloader, "REPOS_DIR", tmp_path / "repos")
    monkeypatch.setattr(repo_downloader, "ensure_runtime_directories", lambda: None)

    root = repo_downloader._checkout_root()
    assert root == (tmp_path / "repos" / "audit-comp-ens").resolve()


def test_prepare_checkout_requires_exact_commit(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Downloader must reject a worktree that resolves to a different commit."""

    checkout = tmp_path / "audit-comp-ens"
    (checkout / ".git").mkdir(parents=True)
    monkeypatch.setattr(repo_downloader, "_checkout_root", lambda: checkout)
    monkeypatch.setattr(repo_downloader, "ACTIVE_UPSTREAM_COMMIT", "a" * 40)

    def fake_git(args: list[str], *, cwd: Path | None = None, timeout_s: int = 300) -> str:
        del cwd, timeout_s
        return "b" * 40 if args[:2] == ["rev-parse", "HEAD"] else ""

    monkeypatch.setattr(repo_downloader, "_run_git", fake_git)

    with pytest.raises(repo_downloader.RepositoryDownloadError, match="does not match"):
        repo_downloader._prepare_checkout()


def test_build_assets_maps_only_configured_subtrees(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Asset creation must use only configured paths contained by the checkout."""

    root = tmp_path / "repo"
    root.mkdir()
    specs = (
        AssetSpec("one", Path("apps/one")),
        AssetSpec("two", Path("packages/two")),
    )
    for spec in specs:
        (root / spec.relative_path).mkdir(parents=True)
    monkeypatch.setattr(repo_downloader, "ASSETS", specs)
    monkeypatch.setattr(repo_downloader, "ACTIVE_UPSTREAM_COMMIT", "c" * 40)

    assets = repo_downloader._build_assets(root)
    assert [asset.name for asset in assets] == ["one", "two"]
    assert all(asset.commit == "c" * 40 for asset in assets)


def test_build_assets_rejects_missing_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A missing configured asset must abort the asset map."""

    root = tmp_path / "repo"
    root.mkdir()
    monkeypatch.setattr(
        repo_downloader,
        "ASSETS",
        (AssetSpec("missing", Path("missing")),),
    )

    with pytest.raises(repo_downloader.RepositoryDownloadError, match="missing"):
        repo_downloader._build_assets(root)


@pytest.mark.asyncio
async def test_download_all_repos_returns_assets(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Async downloader must return the validated asset list from its worker threads."""

    expected = [Asset("manager", tmp_path, "d" * 40)]
    monkeypatch.setattr(repo_downloader, "_prepare_checkout", lambda: tmp_path)
    monkeypatch.setattr(repo_downloader, "_build_assets", lambda _: expected)

    assert await repo_downloader.download_all_repos() == expected

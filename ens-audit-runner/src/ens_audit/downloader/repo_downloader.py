"""Acquire the pinned ENS audit source tree and expose its five scoped assets."""

from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
from pathlib import Path

from ens_audit.config import (
    ACTIVE_UPSTREAM_COMMIT,
    ASSETS,
    REPOS_DIR,
    UPSTREAM_BRANCH,
    UPSTREAM_REPOSITORY,
    ensure_runtime_directories,
)
from ens_audit.models import Asset


class RepositoryDownloadError(RuntimeError):
    """Raised when the immutable audit checkout cannot be prepared safely."""


def _git_executable() -> str:
    """Return the locally installed Git executable.

    Security invariant: command execution uses an executable resolved by ``shutil.which``
    and never invokes a shell.
    """

    executable = shutil.which("git")
    if executable is None:
        raise RepositoryDownloadError("git executable was not found on PATH")
    return executable


def _run_git(args: list[str], *, cwd: Path | None = None, timeout_s: int = 300) -> str:
    """Run one Git command as an argv list and return stdout.

    Security invariant: Git is always invoked with ``shell=False`` and arguments are passed
    as discrete tokens, so repository metadata cannot become shell syntax.
    """

    completed = subprocess.run(
        [_git_executable(), *args],
        cwd=cwd,
        shell=False,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_s,
        env={
            "PATH": os.environ.get("PATH", ""),
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_CONFIG_NOSYSTEM": "1",
        },
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or "git command failed"
        raise RepositoryDownloadError(message[:1000])
    return completed.stdout.strip()


def _checkout_root() -> Path:
    """Return the fixed local checkout path.

    Security invariant: the checkout location is always a direct child of ``REPOS_DIR``.
    """

    ensure_runtime_directories()
    root = (REPOS_DIR / "audit-comp-ens").resolve()
    repos_root = REPOS_DIR.resolve()
    if not root.is_relative_to(repos_root):
        raise RepositoryDownloadError("checkout path escaped repository cache")
    if root.is_symlink():
        raise RepositoryDownloadError("checkout path must not be a symlink")
    return root


def _prepare_checkout() -> Path:
    """Clone or refresh the upstream repository and detach at the verified commit.

    Security invariant: the final worktree must report exactly ``ACTIVE_UPSTREAM_COMMIT``
    before any asset is returned to the analysis pipeline.
    """

    root = _checkout_root()
    git_dir = root / ".git"
    if not git_dir.exists():
        if root.exists() and any(root.iterdir()):
            raise RepositoryDownloadError("checkout directory exists but is not a Git repository")
        root.parent.mkdir(parents=True, exist_ok=True)
        _run_git(
            [
                "clone",
                "--branch",
                UPSTREAM_BRANCH,
                "--no-checkout",
                UPSTREAM_REPOSITORY,
                str(root),
            ]
        )
    else:
        _run_git(["fetch", "--prune", "origin", UPSTREAM_BRANCH], cwd=root)

    _run_git(["checkout", "--detach", ACTIVE_UPSTREAM_COMMIT], cwd=root)
    actual = _run_git(["rev-parse", "HEAD"], cwd=root)
    if actual != ACTIVE_UPSTREAM_COMMIT:
        raise RepositoryDownloadError("checked-out commit does not match configured audit commit")
    return root


def _contains_solidity(asset_path: Path) -> bool:
    """Return whether an asset contains a Solidity source file.

    Security invariant: directory symlinks are not followed while inspecting the asset.
    """

    for current, directories, files in os.walk(asset_path, followlinks=False):
        directories[:] = [
            name for name in directories if not (Path(current) / name).is_symlink()
        ]
        if any(name.endswith(".sol") for name in files):
            return True
    return False


def _build_assets(root: Path) -> list[Asset]:
    """Map configured repository-relative asset paths to validated local assets.

    Security invariant: every resolved asset path must remain inside the pinned checkout.
    """

    resolved_root = root.resolve()
    assets: list[Asset] = []
    for spec in ASSETS:
        asset_path = (resolved_root / spec.relative_path).resolve()
        if not asset_path.is_relative_to(resolved_root) or not asset_path.is_dir():
            raise RepositoryDownloadError(f"configured asset path is invalid: {spec.name}")
        assets.append(
            Asset(
                name=spec.name,
                path=asset_path,
                commit=ACTIVE_UPSTREAM_COMMIT,
                has_solidity=_contains_solidity(asset_path),
            )
        )
    return assets


async def download_all_repos() -> list[Asset]:
    """Prepare the pinned checkout and return all five scoped assets.

    Security invariant: callers receive assets only after exact-commit verification and path
    containment checks complete successfully.
    """

    root = await asyncio.to_thread(_prepare_checkout)
    return await asyncio.to_thread(_build_assets, root)

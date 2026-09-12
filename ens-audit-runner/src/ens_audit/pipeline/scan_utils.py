"""Shared bounded source traversal helpers for structural audit stages."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ens_audit.config import RESULTS_DIR
from ens_audit.models import Asset

SOURCE_SUFFIXES = frozenset({
    ".cjs", ".css", ".html", ".htm", ".js", ".jsx", ".json", ".mjs",
    ".py", ".rs", ".sol", ".svelte", ".ts", ".tsx", ".vue",
})
SKIP_PARTS = frozenset({
    ".git", ".next", ".nuxt", ".pytest_cache", ".turbo", "__pycache__",
    "build", "coverage", "dist", "node_modules", "target", "vendor",
})
MAX_FILE_BYTES = 2 * 1024 * 1024


def iter_source_files(asset: Asset) -> list[Path]:
    """Return bounded, regular source files under one validated asset."""
    result: list[Path] = []
    root = asset.path.resolve()
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            relative = path.resolve().relative_to(root)
        except ValueError:
            continue
        if any(part in SKIP_PARTS for part in relative.parts):
            continue
        if path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        result.append(path)
    return sorted(result)


def read_text(path: Path) -> str:
    """Read source text without allowing encoding errors to abort scope coverage."""
    return path.read_text(encoding="utf-8", errors="replace")


def relative_file(asset: Asset, path: Path) -> str:
    """Return a stable slash-separated asset-relative path."""
    return path.resolve().relative_to(asset.path.resolve()).as_posix()


def line_number(text: str, offset: int) -> int:
    """Convert a text offset into a one-based source line."""
    return text.count("\n", 0, max(0, offset)) + 1


def write_coverage(
    asset: Asset,
    stage: str,
    *,
    files: list[Path],
    hits: int,
    extra: dict[str, object] | None = None,
) -> None:
    """Persist explicit scope evidence even when a stage emits zero findings."""
    suffixes = Counter(path.suffix.lower() or "<none>" for path in files)
    payload: dict[str, object] = {
        "asset": asset.name,
        "commit": asset.commit,
        "stage": stage,
        "status": "completed",
        "files_scanned": len(files),
        "rule_hits": hits,
        "extensions": dict(sorted(suffixes.items())),
    }
    if extra:
        payload.update(extra)
    destination = RESULTS_DIR / asset.name / stage
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "coverage.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

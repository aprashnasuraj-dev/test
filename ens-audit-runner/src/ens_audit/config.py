"""Static configuration for ENS Audit Runner.

Security invariant: repository, tool, and output paths are centralized here so pipeline
stages do not invent or silently redirect audit scope at runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

APP_NAME = "ENS Audit Runner"
UPSTREAM_REPOSITORY = "https://github.com/immunefi-team/audit-comp-ens.git"
UPSTREAM_BRANCH = "audit-comp-ready"
REQUESTED_UPSTREAM_COMMIT = "63772fd872af472ced58b009499355f3430c2a86"
# VERIFY: requested SHA is not present in immunefi-team/audit-comp-ens as of 2026-09-12.
VERIFIED_UPSTREAM_COMMIT = "1c9b47f18fcddd2e864dfe385c4171061c9811ae"
ACTIVE_UPSTREAM_COMMIT = VERIFIED_UPSTREAM_COMMIT

AUDIT_HOME = Path.home() / "ens-audit"
REPOS_DIR = AUDIT_HOME / "repos"
RESULTS_DIR = AUDIT_HOME / "results"
DATABASE_PATH = AUDIT_HOME / "audit.sqlite3"
LOG_PATH = AUDIT_HOME / "ens-audit.log"

PIPELINE_STAGES = (
    "sast",
    "symbolic",
    "fuzz",
    "deps",
    "secrets",
    "known_filter",
    "report",
)

REQUIRED_TOOLS = (
    "git",
    "codeql",
    "semgrep",
    "slither",
    "myth",
    "halmos",
    "forge",
    "echidna",
    "npm",
    "npx",
    "pip-audit",
    "trufflehog",
    "detect-secrets",
)


@dataclass(frozen=True, slots=True)
class AssetSpec:
    """Describe one immutable audit asset.

    Security invariant: every asset is constrained to a repository-relative path and a
    fixed logical name used consistently in findings and reports.
    """

    name: str
    relative_path: Path


ASSETS = (
    AssetSpec("manager", Path("apps/manager")),
    # ASSUMPTION: competition scope label "Explorer" maps to the checked-in portal app.
    AssetSpec("explorer", Path("apps/portal")),
    AssetSpec("workers", Path("workers")),
    AssetSpec("transaction-manager", Path("packages/transaction-manager")),
    AssetSpec("smart-account", Path("packages/smart-account")),
)


def ensure_runtime_directories() -> None:
    """Create runner-owned runtime directories without modifying audited source trees.

    Security invariant: only the fixed runner home, repo cache, and result directories are
    created; arbitrary caller-supplied paths are never accepted here.
    """

    for path in (AUDIT_HOME, REPOS_DIR, RESULTS_DIR):
        path.mkdir(parents=True, exist_ok=True)

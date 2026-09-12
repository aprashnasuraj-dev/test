"""Commit-diff security review for every configured audit asset."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ens_audit.config import RESULTS_DIR
from ens_audit.models import Asset, Finding, Location, Severity


@dataclass(frozen=True, slots=True)
class _Risk:
    rule_id: str
    pattern: re.Pattern[str]
    title: str
    severity: Severity
    root_cause: str
    recommendation: str


_RISKS = (
    _Risk(
        "diff-dynamic-execution",
        re.compile(
            r"\b(?:eval\s*\(|exec\s*\(|new\s+Function\s*\(|child_process|"
            r"spawn\s*\(|execFile\s*\()",
            re.IGNORECASE,
        ),
        "Security-sensitive change introduces an execution primitive",
        Severity.HIGH,
        "changed_dynamic_execution_surface",
        "Trace every newly introduced value reaching the execution primitive and replace string-based execution with explicit APIs.",
    ),
    _Risk(
        "diff-html-sink",
        re.compile(
            r"(?:innerHTML|outerHTML|insertAdjacentHTML|dangerouslySetInnerHTML|document\.write)",
            re.IGNORECASE,
        ),
        "Security-sensitive change touches an HTML parsing sink",
        Severity.MEDIUM,
        "changed_html_injection_surface",
        "Verify the new data flow cannot contain attacker-controlled markup; prefer non-HTML rendering APIs.",
    ),
    _Risk(
        "diff-solidity-call",
        re.compile(
            r"\.(?:delegatecall|call|staticcall)\s*(?:\{|\()|"
            r"\bselfdestruct\s*\(|\btx\.origin\b|\bassembly\s*\{",
            re.IGNORECASE,
        ),
        "Security-sensitive change touches a low-level Solidity primitive",
        Severity.HIGH,
        "changed_low_level_contract_primitive",
        "Review authorization, call target control, reentrancy, storage layout, revert handling, and value flow for the changed primitive.",
    ),
    _Risk(
        "diff-auth-signature",
        re.compile(
            r"\b(?:authorize|authorization|permission|role|owner|signature|recover|nonce|"
            r"chainId|chain_id|session|impersonat|privilege|accessControl)\b",
            re.IGNORECASE,
        ),
        "Change modifies an authorization or signature boundary",
        Severity.MEDIUM,
        "changed_authorization_boundary",
        "Re-derive the trust assumptions and test unauthorized, replay, cross-chain/domain, stale-session, and privilege-escalation cases.",
    ),
    _Risk(
        "diff-rpc-network",
        re.compile(
            r"\b(?:provider\.request|jsonrpc|rpc|fetch\s*\(|WebSocket\s*\(|url|"
            r"endpoint|redirect)\b",
            re.IGNORECASE,
        ),
        "Change modifies an RPC or outbound network boundary",
        Severity.MEDIUM,
        "changed_rpc_network_boundary",
        "Review method/parameter validation, endpoint allowlists, redirects, credentials, origin checks, and timeout/error handling.",
    ),
    _Risk(
        "diff-secret-key",
        re.compile(
            r"\b(?:secret|token|api[_-]?key|private[_-]?key|mnemonic|seed|credential)\b",
            re.IGNORECASE,
        ),
        "Change modifies secret or key material handling",
        Severity.MEDIUM,
        "changed_secret_handling",
        "Confirm secrets are not logged or persisted insecurely and that key material never crosses an unintended trust boundary.",
    ),
)

_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(?P<line>\d+)(?:,\d+)? @@")


def _repo_root(path: Path) -> Path:
    process = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if process.returncode != 0:
        raise RuntimeError(f"git root lookup failed: {process.stderr.strip()}")
    return Path(process.stdout.strip()).resolve()


def _first_parent(repo: Path, commit: str) -> str:
    process = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"{commit}^"],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if process.returncode != 0:
        raise RuntimeError(f"parent commit unavailable for {commit}: {process.stderr.strip()}")
    return process.stdout.strip()


def _diff(repo: Path, parent: str, commit: str, scope: str) -> str:
    process = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "diff",
            "--no-ext-diff",
            "--unified=0",
            "--find-renames",
            parent,
            commit,
            "--",
            scope,
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )
    if process.returncode != 0:
        raise RuntimeError(f"git diff failed: {process.stderr.strip()}")
    return process.stdout


class DiffStage:
    """Review added/changed lines at the pinned revision for security-sensitive deltas."""

    async def run(self, asset: Asset) -> list[Finding]:
        """Analyze the asset's pinned commit against its first parent."""
        repo = _repo_root(asset.path)
        parent = _first_parent(repo, asset.commit)
        scope = asset.path.resolve().relative_to(repo).as_posix()
        patch = _diff(repo, parent, asset.commit, scope)

        current_file = ""
        current_line = 0
        changed_files: set[str] = set()
        added_lines = 0
        findings: list[Finding] = []
        seen: set[tuple[str, str]] = set()

        for raw in patch.splitlines():
            if raw.startswith("+++ b/"):
                current_file = raw[6:]
                changed_files.add(current_file)
                continue
            hunk = _HUNK.match(raw)
            if hunk:
                current_line = int(hunk.group("line"))
                continue
            if raw.startswith("+") and not raw.startswith("+++"):
                added_lines += 1
                source = raw[1:]
                for risk in _RISKS:
                    if not risk.pattern.search(source):
                        continue
                    key = (current_file, risk.rule_id)
                    if key in seen:
                        continue
                    seen.add(key)
                    asset_relative = current_file
                    prefix = f"{scope}/" if scope != "." else ""
                    if prefix and current_file.startswith(prefix):
                        asset_relative = current_file[len(prefix) :]
                    findings.append(
                        Finding(
                            title=risk.title,
                            severity=risk.severity,
                            asset=asset.name,
                            stage="diff",
                            rule_id=risk.rule_id,
                            root_cause=risk.root_cause,
                            location=Location(asset_relative or current_file, current_line),
                            description=(
                                "The pinned revision adds or changes a line matching a "
                                "security-sensitive pattern. This is a review signal tied to "
                                "the exact commit diff, not proof of exploitability by itself."
                            ),
                            evidence=f"changed line matched security category {risk.rule_id}",
                            impact=(
                                "A regression in this changed trust boundary could introduce "
                                "a new vulnerability relative to the parent revision."
                            ),
                            recommendation=risk.recommendation,
                            confidence=0.62,
                        )
                    )
                current_line += 1
            elif raw.startswith("-") and not raw.startswith("---"):
                continue
            elif raw and not raw.startswith("\\"):
                current_line += 1

        destination = RESULTS_DIR / asset.name / "diff"
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "coverage.json").write_text(
            json.dumps(
                {
                    "asset": asset.name,
                    "stage": "diff",
                    "status": "completed",
                    "base_commit": parent,
                    "head_commit": asset.commit,
                    "scope": scope,
                    "changed_files": sorted(changed_files),
                    "changed_file_count": len(changed_files),
                    "added_lines": added_lines,
                    "rule_hits": len(findings),
                    "rules_evaluated": len(_RISKS),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return findings

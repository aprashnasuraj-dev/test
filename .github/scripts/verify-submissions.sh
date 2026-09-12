#!/usr/bin/env bash
set -euo pipefail

ROOT="${OUT_DIR:-${GITHUB_WORKSPACE}/staging}"
[[ -d "$ROOT" ]] || { echo "::error::Submission root not found: $ROOT"; exit 1; }
export SUBMISSION_ROOT="$ROOT"

python - <<'PY'
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

root = Path(os.environ["SUBMISSION_ROOT"]).resolve()
findings_dir = root / "findings"
subs_dir = root / "submissions"
pocs_dir = root / "pocs"

required_files = [
    root / "MANIFEST.json",
    root / "SUBMISSION-CHECKLIST.md",
    findings_dir / "findings_escaped.json",
    findings_dir / "findings_new.json",
]
missing_root = [str(p.relative_to(root)) for p in required_files if not p.is_file()]
if missing_root:
    print("::error::Missing required staged files: " + ", ".join(missing_root))
    sys.exit(1)

required_markers = [
    "**Severity:**",
    "**Asset:**",
    "**Impact:**",
    "## Summary",
    "## Vulnerability Detail",
    "## Impact",
    "## Proof of Concept",
    "## Recommendation",
    "## References",
]

print("file | sections_ok | missing")
print("--- | --- | ---")
section_failures: list[str] = []
for path in sorted(subs_dir.glob("*.md")):
    text = path.read_text(encoding="utf-8", errors="replace")
    first_line = text.splitlines()[0] if text.splitlines() else ""
    missing: list[str] = []
    if not first_line.startswith("# ") or first_line.startswith("## "):
        missing.append("# <title>")
    positions = []
    for marker in required_markers:
        pos = text.find(marker)
        positions.append(pos)
        if pos < 0:
            missing.append(marker)
    present_positions = [pos for pos in positions if pos >= 0]
    if not missing and present_positions != sorted(present_positions):
        missing.append("heading order")
    ok = not missing
    print(f"{path.name} | {'yes' if ok else 'no'} | {', '.join(missing) if missing else '-'}")
    if not ok:
        section_failures.append(path.name)


def load(name: str) -> list[dict[str, Any]]:
    path = findings_dir / name
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("findings", [])
    if not isinstance(items, list):
        raise SystemExit(f"{path} must contain a findings list")
    return [item for item in items if isinstance(item, dict)]


def fid(finding: dict[str, Any]) -> str:
    return str(
        finding.get("id") or finding.get("finding_id") or finding.get("rule_id") or ""
    ).strip()

required: dict[str, dict[str, Any]] = {}
for finding in load("findings_new.json") + load("findings_escaped.json"):
    if str(finding.get("severity", "")).lower() not in {"critical", "high", "medium"}:
        continue
    status = str(finding.get("status", "open")).lower()
    if status in {"suppressed", "false_positive", "duplicate"} or finding.get("duplicate") is True:
        continue
    finding_id = fid(finding)
    if not finding_id:
        print("::error::Actionable finding is missing an id")
        sys.exit(1)
    required.setdefault(finding_id, finding)

artifact_failures: list[str] = []
for finding_id in sorted(required):
    submission = subs_dir / f"{finding_id}.md"
    poc = pocs_dir / finding_id
    if not submission.is_file():
        artifact_failures.append(f"{finding_id}: missing submissions/{finding_id}.md")
    if not poc.is_dir():
        artifact_failures.append(f"{finding_id}: missing pocs/{finding_id}/")
        continue
    for name in ("README.md", "finding.json", "verify.py", "run.sh", "run.ps1", "run.log"):
        if not (poc / name).is_file():
            artifact_failures.append(f"{finding_id}: missing pocs/{finding_id}/{name}")
    log = poc / "run.log"
    if log.is_file() and "POC_OK" not in log.read_text(encoding="utf-8", errors="replace"):
        artifact_failures.append(f"{finding_id}: pocs/{finding_id}/run.log missing POC_OK")

if section_failures or artifact_failures:
    for failure in artifact_failures:
        print(f"::error::{failure}")
    if section_failures:
        print("::error::Submission section validation failed: " + ", ".join(section_failures))
    sys.exit(1)

print(f"OK — {len(list(subs_dir.glob('*.md')))} submissions validated.")
print(f"OK — {len(required)} non-duplicate Critical/High/Medium finding(s) have PoCs.")
PY

#!/usr/bin/env bash
set -euo pipefail

SRC="${OUT_DIR:-${GITHUB_WORKSPACE}/out}"
ALT="${GITHUB_WORKSPACE}/ens-audit-runner/out"
[[ -d "$SRC" ]] || SRC="$ALT"
[[ -d "$SRC" ]] || { echo "no output"; exit 0; }

DST="${GITHUB_WORKSPACE}/staging"
rm -rf "$DST"
mkdir -p "$DST"/{findings,submissions,pocs,insights,runs}

for f in findings.json findings_new.json findings_escaped.json \
         findings_suppressed.json findings_informational.json \
         findings_rejected.json; do
  [[ -f "$SRC/$f" ]] && cp "$SRC/$f" "$DST/findings/" || true
done

[[ -d "$SRC/submissions" ]] && cp -r "$SRC/submissions/." "$DST/submissions/" || true
[[ -d "$SRC/pocs"        ]] && cp -r "$SRC/pocs/."        "$DST/pocs/"        || true
[[ -d "$SRC/insights"    ]] && cp -r "$SRC/insights/."    "$DST/insights/"    || true
[[ -d "$SRC/runs" ]] && cp -r "$SRC/runs/." "$DST/runs/" || true
for log in "$SRC"/*.log; do
  [[ -f "$log" ]] && cp "$log" "$DST/runs/" || true
done

python - "$DST" <<'PY'
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

dst = Path(sys.argv[1])
findings_dir = dst / "findings"


def load(name: str) -> list[dict[str, Any]]:
    path = findings_dir / name
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    items = data if isinstance(data, list) else data.get("findings", [])
    return [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []


def sid(finding: dict[str, Any]) -> str:
    return str(
        finding.get("id") or finding.get("finding_id") or finding.get("rule_id") or "unknown"
    )


def is_actionable(finding: dict[str, Any]) -> bool:
    if str(finding.get("severity", "")).lower() not in {"critical", "high", "medium"}:
        return False
    status = str(finding.get("status", "open")).lower()
    return status not in {"suppressed", "false_positive", "duplicate"} and finding.get("duplicate") is not True

buckets = {
    "new": load("findings_new.json"),
    "escaped": load("findings_escaped.json"),
    "suppressed": load("findings_suppressed.json"),
    "informational": load("findings_informational.json"),
    "rejected": load("findings_rejected.json"),
}

actionable_by_id: dict[str, dict[str, Any]] = {}
for finding in buckets["new"] + buckets["escaped"]:
    if is_actionable(finding):
        actionable_by_id.setdefault(sid(finding), finding)

actionable = []
ready: list[str] = []
incomplete: list[str] = []
for finding_id, finding in sorted(actionable_by_id.items()):
    submission = dst / "submissions" / f"{finding_id}.md"
    poc_dir = dst / "pocs" / finding_id
    entry = {
        "id": finding_id,
        "severity": finding.get("severity"),
        "asset": finding.get("asset") or finding.get("asset_role"),
        "file": (finding.get("location") or {}).get("file") or finding.get("file"),
        "line": (finding.get("location") or {}).get("line") or finding.get("line_start") or finding.get("line"),
        "impact": finding.get("impact"),
        "matched_known_id": finding.get("matched_known_id"),
        "escape_reason": finding.get("escape_reason"),
        "submission": f"submissions/{finding_id}.md" if submission.is_file() else None,
        "poc_dir": f"pocs/{finding_id}" if poc_dir.is_dir() else None,
    }
    actionable.append(entry)
    if entry["submission"] and entry["poc_dir"]:
        ready.append(finding_id)
    else:
        incomplete.append(finding_id)

run_url = (
    f"{os.environ.get('GITHUB_SERVER_URL', '')}/{os.environ.get('GITHUB_REPOSITORY', '')}"
    f"/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
)
manifest = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "run": {
        "repository": os.environ.get("GITHUB_REPOSITORY"),
        "sha": os.environ.get("GITHUB_SHA"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER"),
        "run_url": run_url,
    },
    "counts": {key: len(value) for key, value in buckets.items()},
    "actionable": actionable,
    "submission_ready": ready,
    "submission_incomplete": incomplete,
    "insights": [
        {"id": sid(f), "file": f"insights/{sid(f)}.md"}
        for f in buckets["informational"]
        if (dst / "insights" / f"{sid(f)}.md").exists()
    ],
}
(dst / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

lines = [
    "# Submission Checklist",
    "",
    f"- Run: {run_url}",
    f"- Commit: `{manifest['run']['sha']}`",
    f"- Generated: {manifest['generated_at']}",
    "",
    "## Non-duplicate Critical / High / Medium findings",
    "",
]
ready_set = set(ready)
for entry in actionable:
    box = "[x]" if entry["id"] in ready_set else "[ ]"
    missing = []
    if not entry["submission"]:
        missing.append("submission")
    if not entry["poc_dir"]:
        missing.append("poc")
    note = f" — **missing: {', '.join(missing)}**" if missing else ""
    lines.append(
        f"- {box} **{entry['id']}** — {entry.get('severity', '?')} — "
        f"`{entry.get('asset') or '?'}` — {entry.get('file') or '?'}:{entry.get('line') or '?'}{note}"
    )

lines += ["", "## Insights", ""]
for entry in manifest["insights"]:
    lines.append(f"- [ ] **{entry['id']}** — see `{entry['file']}`")
lines += [
    "",
    "## Counts",
    "",
    f"- New: {manifest['counts']['new']}",
    f"- Escaped: {manifest['counts']['escaped']}",
    f"- Suppressed: {manifest['counts']['suppressed']}",
    f"- Informational: {manifest['counts']['informational']}",
    f"- Rejected: {manifest['counts']['rejected']}",
    f"- Submission ready: {len(ready)}",
    f"- Submission incomplete: {len(incomplete)}",
    "",
]
(dst / "SUBMISSION-CHECKLIST.md").write_text("\n".join(lines), encoding="utf-8")

index = f"""# Analysis Run {manifest['run']['run_number']}

- Run page: {run_url}
- Commit: `{manifest['run']['sha']}`
- Generated: {manifest['generated_at']}

## Layout

- `findings/` — normalized finding buckets
- `submissions/` — submission markdown
- `pocs/` — offline proof-of-concept directories
- `insights/` — informational observations
- `runs/` — analyzer and pipeline logs
- `MANIFEST.json` — machine-readable inventory
- `SUBMISSION-CHECKLIST.md` — submission readiness checklist
"""
(dst / "INDEX.md").write_text(index, encoding="utf-8")
(dst / "README.md").write_text(index, encoding="utf-8")

print(f"staged: {dst}")
for path in sorted(dst.rglob("*")):
    if path.is_file():
        print(f"  {path.relative_to(dst)}")
PY

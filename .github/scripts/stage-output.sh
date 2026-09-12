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
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone

dst = Path(sys.argv[1])
findings_dir = dst / "findings"

def load(name):
    p = findings_dir / name
    if not p.exists():
        return []
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
    return d if isinstance(d, list) else d.get("findings", [])

buckets = {
    "new": load("findings_new.json"),
    "escaped": load("findings_escaped.json"),
    "suppressed": load("findings_suppressed.json"),
    "informational": load("findings_informational.json"),
    "rejected": load("findings_rejected.json"),
}

def sid(f):
    return f.get("id") or f.get("finding_id") or f.get("rule_id") or "unknown"

manifest = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "run": {
        "repository": os.environ.get("GITHUB_REPOSITORY"),
        "sha": os.environ.get("GITHUB_SHA"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER"),
        "run_url": f"{os.environ.get('GITHUB_SERVER_URL','')}/{os.environ.get('GITHUB_REPOSITORY','')}/actions/runs/{os.environ.get('GITHUB_RUN_ID','')}",
    },
    "counts": {k: len(v) for k, v in buckets.items()},
    "escaped": [
        {
            "id": sid(f),
            "severity": f.get("severity"),
            "asset": f.get("asset") or f.get("asset_role"),
            "file": f.get("file"),
            "line": f.get("line_start") or f.get("line"),
            "impact": f.get("impact"),
            "matched_known_id": f.get("matched_known_id"),
            "escape_reason": f.get("escape_reason"),
            "submission": f"submissions/{sid(f)}.md" if (dst / "submissions" / f"{sid(f)}.md").exists() else None,
            "poc_dir": f"pocs/{sid(f)}" if (dst / "pocs" / str(sid(f))).is_dir() else None,
        }
        for f in buckets["escaped"]
    ],
    "insights": [
        {"id": sid(f), "file": f"insights/{sid(f)}.md"}
        for f in buckets["informational"]
        if (dst / "insights" / f"{sid(f)}.md").exists()
    ],
    "submission_ready": [],
    "submission_incomplete": [],
}

for e in manifest["escaped"]:
    if str(e.get("severity", "")).lower() not in {"critical", "high", "medium"}:
        continue
    ok = bool(e["submission"]) and bool(e["poc_dir"])
    (manifest["submission_ready"] if ok else manifest["submission_incomplete"]).append(e["id"])

(dst / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

lines = [
    "# Submission Checklist", "",
    f"- Run: {manifest['run']['run_url']}",
    f"- Commit: `{manifest['run']['sha']}`",
    f"- Generated: {manifest['generated_at']}", "",
    "## Escaped findings (Critical / High / Medium)", "",
]
ready = set(manifest["submission_ready"])
incomplete = set(manifest["submission_incomplete"])
for e in manifest["escaped"]:
    sev = str(e.get("severity", "")).lower()
    if sev not in {"critical", "high", "medium"}:
        continue
    box = "[x]" if e["id"] in ready else "[ ]"
    note = ""
    if e["id"] in incomplete:
        missing = []
        if not e["submission"]:
            missing.append("submission")
        if not e["poc_dir"]:
            missing.append("poc")
        note = f" — **missing: {', '.join(missing)}**"
    lines.append(
        f"- {box} **{e['id']}** — {e.get('severity','?')} — "
        f"`{e.get('asset') or '?'}` — {e.get('file') or '?'}:{e.get('line') or '?'}{note}"
    )

lines += ["", "## Insights (informational, eligible for insight pool)", ""]
for e in manifest["insights"]:
    lines.append(f"- [ ] **{e['id']}** — see `{e['file']}`")

lines += [
    "", "## How to submit", "",
    "1. Open the matching `submissions/<id>.md` file.",
    "2. Copy each section into the Immunefi submission form.",
    "3. Attach `pocs/<id>/` as a ZIP.",
    "4. Reference commit SHA in the submission.",
    "5. Submit before **2026-09-14 04:00 UTC**.",
    "", "## Counts", "",
    f"- New: {manifest['counts']['new']}",
    f"- Escaped: {manifest['counts']['escaped']}",
    f"- Suppressed (public known): {manifest['counts']['suppressed']}",
    f"- Informational: {manifest['counts']['informational']}",
    f"- Rejected (out of scope): {manifest['counts']['rejected']}",
    f"- Submission ready: {len(ready)}",
    f"- Submission incomplete: {len(incomplete)}", "",
]
(dst / "SUBMISSION-CHECKLIST.md").write_text("\n".join(lines), encoding="utf-8")

(dst / "README.md").write_text(f"""# Analysis Run {manifest['run']['run_number']}

- Run page: {manifest['run']['run_url']}
- Commit: `{manifest['run']['sha']}`
- Generated: {manifest['generated_at']}

## Layout

- `findings/` — raw finding buckets (json)
- `submissions/` — one Immunefi-format markdown per escaped finding
- `pocs/` — runnable proof-of-concept per escaped finding
- `insights/` — informational observations
- `runs/` — RPC capture logs and stage stdout
- `MANIFEST.json` — machine-readable inventory
- `SUBMISSION-CHECKLIST.md` — tick boxes for the submission workflow

Read `SUBMISSION-CHECKLIST.md` first.
""", encoding="utf-8")

print(f"staged: {dst}")
for p in sorted(dst.rglob("*")):
    if p.is_file():
        print(f"  {p.relative_to(dst)}")
PY

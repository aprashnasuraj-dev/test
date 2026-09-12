#!/usr/bin/env bash
set -euo pipefail

OUT="${OUT_DIR:-${GITHUB_WORKSPACE}/out}"
RUNNER_OUT="${GITHUB_WORKSPACE}/ens-audit-runner/out"

if [[ ! -d "$OUT" && -d "$RUNNER_OUT" ]]; then
  OUT="$RUNNER_OUT"
fi

if [[ ! -d "$OUT" ]]; then
  echo "::error::No output directory found at ${GITHUB_WORKSPACE}/out or $RUNNER_OUT"
  exit 1
fi

ESC="$OUT/findings_escaped.json"
[[ -f "$ESC" ]] || ESC="$OUT/findings/findings_escaped.json"

if [[ ! -f "$ESC" ]]; then
  echo "::warning::findings_escaped.json not produced; skipping submission check"
  echo "This is acceptable if the run only executed a subset of stages."
  exit 0
fi

export ESC_PATH="$ESC"
export OUT_DIR="$OUT"

REQUIRED=$(python - <<'PY'
import json, os
p = os.environ["ESC_PATH"]
try:
    data = json.load(open(p, encoding="utf-8"))
except Exception:
    print(0)
    raise SystemExit
items = data if isinstance(data, list) else data.get("findings", [])
n = sum(1 for f in items
        if str(f.get("severity", "")).lower() in {"critical", "high", "medium"})
print(n)
PY
)

echo "Escaped findings requiring submissions: $REQUIRED"

if [[ "$REQUIRED" -eq 0 ]]; then
  echo "No Critical/High/Medium escaped findings. Nothing to verify."
  exit 0
fi

python - <<'PY'
import json, os, sys
from pathlib import Path

out = Path(os.environ["OUT_DIR"])
esc = Path(os.environ["ESC_PATH"])
data = json.loads(esc.read_text(encoding="utf-8"))
items = data if isinstance(data, list) else data.get("findings", [])
required = [f for f in items
            if str(f.get("severity", "")).lower() in {"critical", "high", "medium"}]

subs_dir = out / "submissions"
pocs_dir = out / "pocs"
missing = []
for finding in required:
    fid = finding.get("id") or finding.get("finding_id") or finding.get("rule_id")
    if not fid:
        missing.append(("unknown", "missing id field"))
        continue
    sub = subs_dir / f"{fid}.md"
    poc = pocs_dir / str(fid)
    if not sub.exists():
        missing.append((fid, f"missing submissions/{fid}.md"))
    if not poc.is_dir():
        missing.append((fid, f"missing pocs/{fid}/"))

if missing:
    print("::error::Submission artifacts incomplete:")
    for fid, why in missing:
        print(f"  - {fid}: {why}")
    sys.exit(1)

print(f"OK — {len(required)} escaped findings have submission + PoC artifacts.")
PY

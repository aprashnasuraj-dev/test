#!/usr/bin/env bash
set -euo pipefail

workspace="${GITHUB_WORKSPACE:-$PWD}"
out_dir="$workspace/out/runs"
mkdir -p "$out_dir"

python - "$out_dir/toolchain.json" <<'PY'
import json
import os
import shutil
import sys
from pathlib import Path

def truthy(name: str) -> bool:
    return os.environ.get(name, "0").lower() in {"1", "true", "yes"}

tools = [
    ("codeql", "sast", True),
    ("semgrep", "sast", True),
    ("slither", "sast", True),
    ("bandit", "sast", True),
    ("myth", "symbolic", True),
    ("halmos", "symbolic", True),
    ("forge", "fuzz", True),
    ("echidna", "fuzz", True),
    ("npm", "deps", True),
    ("pip-audit", "deps", True),
    ("snyk", "deps", truthy("REQUIRE_SNYK")),
    ("trufflehog", "secrets", True),
    ("detect-secrets", "secrets", True),
]
strict = truthy("STRICT_TOOLCHAIN")
records = []
missing = []
for name, stage, required in tools:
    path = shutil.which(name)
    records.append(
        {
            "name": name,
            "stage": stage,
            "required": required,
            "available": path is not None,
            "path": path or "",
        }
    )
    if required and path is None:
        missing.append(name)

payload = {
    "strict": strict,
    "require_snyk": truthy("REQUIRE_SNYK"),
    "snyk_auth_configured": bool(os.environ.get("SNYK_TOKEN")),
    "tools": records,
    "missing_required": missing,
}
Path(sys.argv[1]).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
for record in records:
    marker = "OK" if record["available"] else ("MISSING" if record["required"] else "OPTIONAL-MISSING")
    print(f"{marker:16} {record['stage']:9} {record['name']}")
if missing and strict:
    raise SystemExit("missing required final-audit tools: " + ", ".join(missing))
PY

#!/usr/bin/env bash
set -euo pipefail

OUT="${OUT_DIR:-${GITHUB_WORKSPACE}/out}"
RUNNER_OUT="${GITHUB_WORKSPACE}/ens-audit-runner/out"
[[ -d "$OUT" ]] || OUT="$RUNNER_OUT"
[[ -d "$OUT" ]] || { echo "::error::No output directory found"; exit 1; }

export OUT_DIR="$OUT"
python - <<'PY'
from __future__ import annotations

import json
import os
import stat
import subprocess
from pathlib import Path
from typing import Any

out = Path(os.environ["OUT_DIR"]).resolve()
repo_root = (Path.home() / "ens-audit" / "repos" / "audit-comp-ens").resolve()
pocs_root = out / "pocs"
pocs_root.mkdir(parents=True, exist_ok=True)

asset_paths = {
    "manager": "apps/manager",
    "explorer": "apps/portal",
    "portal": "apps/portal",
    "workers": "workers",
    "transaction-manager": "packages/transaction-manager",
    "smart-account": "packages/smart-account",
}

def load_bucket(name: str) -> list[dict[str, Any]]:
    candidates = [out / name, out / "findings" / name]
    path = next((p for p in candidates if p.is_file()), None)
    if path is None:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("findings", [])
    if not isinstance(items, list):
        raise SystemExit(f"{path} must contain a findings list")
    return [item for item in items if isinstance(item, dict)]

def finding_id(finding: dict[str, Any]) -> str:
    return str(
        finding.get("id") or finding.get("finding_id") or finding.get("rule_id") or ""
    ).strip()

candidates = load_bucket("findings_new.json") + load_bucket("findings_escaped.json")
required_by_id: dict[str, dict[str, Any]] = {}
for finding in candidates:
    if str(finding.get("severity", "")).lower() not in {"critical", "high", "medium"}:
        continue
    status = str(finding.get("status", "open")).lower()
    if status in {"suppressed", "false_positive", "duplicate"} or finding.get("duplicate") is True:
        continue
    fid = finding_id(finding)
    if not fid:
        raise SystemExit("actionable finding is missing an id")
    required_by_id.setdefault(fid, finding)
required = list(required_by_id.values())

verify_source = r'''from __future__ import annotations

import json
import sys
from pathlib import Path

ASSET_PATHS = {
    "manager": "apps/manager",
    "explorer": "apps/portal",
    "portal": "apps/portal",
    "workers": "workers",
    "transaction-manager": "packages/transaction-manager",
    "smart-account": "packages/smart-account",
}

here = Path(__file__).resolve().parent
finding = json.loads((here / "finding.json").read_text(encoding="utf-8"))
root = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else (
    Path.home() / "ens-audit" / "repos" / "audit-comp-ens"
).resolve()
asset = str(finding.get("asset", ""))
relative_asset = ASSET_PATHS.get(asset)
if relative_asset is None:
    raise SystemExit(f"POC_FAIL unknown asset: {asset}")
asset_root = (root / relative_asset).resolve()
location = finding.get("location") or {}
relative_file = str(location.get("file", "")).replace("\\", "/")
if not relative_file:
    raise SystemExit("POC_FAIL finding has no source file")
source = (asset_root / relative_file).resolve()
if not source.is_relative_to(asset_root):
    raise SystemExit("POC_FAIL source path escaped asset root")
if not source.is_file():
    raise SystemExit(f"POC_FAIL source file missing: {source}")
lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
line_number = int(location.get("line", 0) or 0)
if line_number < 1 or line_number > len(lines):
    raise SystemExit(f"POC_FAIL invalid source line: {line_number}")
source_line = lines[line_number - 1].strip()
evidence = str(finding.get("evidence", "")).strip()
print(f"finding_id={finding.get('id')}")
print(f"severity={finding.get('severity')}")
print(f"asset={asset}")
print(f"rule_id={finding.get('rule_id')}")
print(f"matched_known_id={finding.get('matched_known_id')}")
print(f"escape_reason={finding.get('escape_reason')}")
print(f"source={relative_asset}/{relative_file}:{line_number}")
print(f"source_line={source_line}")
if evidence:
    print(f"scanner_evidence={evidence}")
    normalized_line = " ".join(source_line.split())
    normalized_evidence = " ".join(evidence.split())
    print(f"evidence_exact_line_match={normalized_evidence == normalized_line}")
print("POC_OK offline source trace reproduced")
'''

for finding in required:
    fid = finding_id(finding)
    if "/" in fid or "\\" in fid or fid in {".", ".."}:
        raise SystemExit(f"invalid finding id for PoC directory: {fid!r}")
    poc = (pocs_root / fid).resolve()
    if not poc.is_relative_to(pocs_root.resolve()):
        raise SystemExit(f"PoC path escaped output root: {fid}")
    poc.mkdir(parents=True, exist_ok=True)
    (poc / "finding.json").write_text(
        json.dumps(finding, indent=2, sort_keys=True), encoding="utf-8"
    )
    (poc / "verify.py").write_text(verify_source, encoding="utf-8")

    location = finding.get("location") or {}
    source_label = (
        f"{finding.get('asset', '?')}/{location.get('file', '?')}:{location.get('line', '?')}"
    )
    readme = "\n".join(
        [
            f"# Offline PoC — {fid}",
            "",
            f"- Severity: **{finding.get('severity', '?')}**",
            f"- Asset: `{finding.get('asset', '?')}`",
            f"- Rule: `{finding.get('rule_id', '?')}`",
            f"- Source: `{source_label}`",
            f"- Matched public issue: `{finding.get('matched_known_id') or 'none'}`",
            f"- Escape reason: `{finding.get('escape_reason') or 'none'}`",
            "",
            "This PoC is intentionally offline and non-destructive. It reproduces the exact",
            "source trace recorded by the analyzer against the pinned audit checkout.",
            "",
            "## Run",
            "",
            "```bash",
            "bash run.sh /path/to/audit-comp-ens",
            "```",
            "",
            "A successful reproduction prints `POC_OK`.",
            "",
        ]
    )
    (poc / "README.md").write_text(readme, encoding="utf-8")

    run_sh = """#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${1:-$HOME/ens-audit/repos/audit-comp-ens}"
python3 "$HERE/verify.py" "$ROOT"
"""
    sh_path = poc / "run.sh"
    sh_path.write_text(run_sh, encoding="utf-8")
    sh_path.chmod(sh_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    run_ps1 = r'''$ErrorActionPreference = "Stop"
$Root = if ($args.Count -gt 0) { $args[0] } else { Join-Path $HOME "ens-audit/repos/audit-comp-ens" }
python (Join-Path $PSScriptRoot "verify.py") $Root
exit $LASTEXITCODE
'''
    (poc / "run.ps1").write_text(run_ps1, encoding="utf-8")

    completed = subprocess.run(
        ["bash", str(sh_path), str(repo_root)],
        shell=False,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    log = completed.stdout
    if completed.stderr:
        log += ("\n" if log and not log.endswith("\n") else "") + completed.stderr
    (poc / "run.log").write_text(log, encoding="utf-8")
    if completed.returncode != 0 or "POC_OK" not in log:
        print(f"::error::PoC failed for {fid}")
        print(log)
        raise SystemExit(1)
    print(f"PoC ready: {fid}")

print(f"Generated and executed {len(required)} offline PoC(s).")
PY

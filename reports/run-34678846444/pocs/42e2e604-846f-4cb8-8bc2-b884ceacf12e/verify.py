from __future__ import annotations

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

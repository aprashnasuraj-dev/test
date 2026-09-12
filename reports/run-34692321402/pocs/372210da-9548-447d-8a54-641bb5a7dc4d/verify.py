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
if not asset_root.is_dir():
    raise SystemExit(f"POC_FAIL asset root missing: {asset_root}")

location = finding.get("location") or {}
if not isinstance(location, dict):
    location = {}
relative_file = str(location.get("file", "")).replace("\\", "/").strip()
line_number = int(location.get("line", 0) or 0)
evidence = str(finding.get("evidence", "")).strip()

print(f"finding_id={finding.get('id')}")
print(f"severity={finding.get('severity')}")
print(f"asset={asset}")
print(f"stage={finding.get('stage')}")
print(f"rule_id={finding.get('rule_id')}")
print(f"matched_known_id={finding.get('matched_known_id')}")
print(f"escape_reason={finding.get('escape_reason')}")

source_verified = False
if relative_file and line_number > 0:
    raw_path = Path(relative_file)
    source_candidates: list[Path] = []
    if raw_path.is_absolute():
        source_candidates.append(raw_path.resolve())
        marker = f"/{relative_asset.strip('/')}/"
        normalized = raw_path.as_posix()
        if marker in normalized:
            suffix = normalized.split(marker, 1)[1]
            source_candidates.append((asset_root / suffix).resolve())
    else:
        source_candidates.append((root / raw_path).resolve())
        source_candidates.append((asset_root / raw_path).resolve())

    source: Path | None = None
    for candidate in source_candidates:
        if candidate.is_relative_to(asset_root) and candidate.is_file():
            source = candidate
            break

    if source is not None:
        lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
        if line_number <= len(lines):
            source_line = lines[line_number - 1].strip()
            try:
                source_label = source.relative_to(root).as_posix()
            except ValueError:
                source_label = source.as_posix()
            print(f"source={source_label}:{line_number}")
            print(f"source_line={source_line}")
            if evidence:
                normalized_line = " ".join(source_line.split())
                normalized_evidence = " ".join(evidence.split())
                print(f"evidence_exact_line_match={normalized_evidence == normalized_line}")
            source_verified = True
        else:
            print(f"source_trace_status=line_out_of_range:{relative_file}:{line_number}")
    else:
        print(f"source_trace_status=not_present_in_current_asset:{relative_file}:{line_number}")
elif relative_file:
    print(f"source_hint={relative_file}")
    print("source_trace_status=no_positive_line_number")
else:
    print("source_trace_status=no_concrete_source_location")

if evidence:
    print(f"scanner_evidence={evidence}")
print(f"source_trace_verified={str(source_verified).lower()}")
print("POC_OK offline finding metadata reproduced")

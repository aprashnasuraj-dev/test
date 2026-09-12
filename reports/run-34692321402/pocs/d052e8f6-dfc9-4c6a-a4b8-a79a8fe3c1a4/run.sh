#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${1:-$HOME/ens-audit/repos/audit-comp-ens}"
python3 "$HERE/verify.py" "$ROOT"

#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_REPO="${UPSTREAM_REPO:-https://github.com/immunefi-team/audit-comp-ens.git}"
UPSTREAM_REF="${UPSTREAM_REF:-audit-comp-ready}"
ROOT_DIR="$(git rev-parse --show-toplevel)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

printf '==> Syncing %s@%s into %s\n' "$UPSTREAM_REPO" "$UPSTREAM_REF" "$ROOT_DIR"
git clone --depth 1 --branch "$UPSTREAM_REF" "$UPSTREAM_REPO" "$TMP_DIR/upstream"

rsync -a --delete \
  --exclude='.git/' \
  --exclude='.github/workflows/bootstrap-ens-audit.yml' \
  --exclude='scripts/bootstrap-audit-workspace.sh' \
  --exclude='scripts/dev-audit-stack.sh' \
  --exclude='tooling/' \
  "$TMP_DIR/upstream/" "$ROOT_DIR/"

cd "$ROOT_DIR"

python3 - <<'PY'
from pathlib import Path
p = Path('pnpm-workspace.yaml')
text = p.read_text()
entry = '  - tooling/*\n'
if entry not in text:
    text = text.replace('packages:\n', 'packages:\n' + entry, 1)
p.write_text(text)
PY

PM_SPEC="$(node -p "require('./package.json').packageManager || 'pnpm@10.27.0'")"
printf '==> Package manager: %s\n' "$PM_SPEC"
corepack enable
corepack prepare "$PM_SPEC" --activate

# Reconcile the upstream lockfile with the local audit tooling packages.
pnpm install --lockfile-only --no-frozen-lockfile

printf '==> Bootstrap sync complete.\n'

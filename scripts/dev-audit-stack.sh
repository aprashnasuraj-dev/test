#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_DIR="${WORKSPACE_DIR:-$ROOT_DIR/ens-workspace}"

if [[ ! -d "$WORKSPACE_DIR/.git" ]]; then
  echo "Missing $WORKSPACE_DIR. Run scripts/bootstrap-local.sh first." >&2
  exit 1
fi

cd "$WORKSPACE_DIR"

cleanup() {
  jobs -p | xargs -r kill 2>/dev/null || true
  pnpm e2e:infra:down >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

pnpm e2e:infra:up

pnpm dev:manager &
MANAGER_PID=$!

(
  cd apps/portal
  pnpm dev
) &
PORTAL_PID=$!

pnpm --filter api-worker dev &
WORKER_PID=$!

cat <<'EOF'

ENS audit development stack started.
- Local Sepolia fork: http://127.0.0.1:8545
- ERC-4337 bundler:   http://127.0.0.1:4337
- Mock orchestrator:  http://127.0.0.1:3007
- DQA service:        http://127.0.0.1:4000

Manager, Portal, and API Worker ports are printed by their dev processes.
Press Ctrl+C to terminate the app processes and tear down the E2E infrastructure.
EOF

wait "$MANAGER_PID" "$PORTAL_PID" "$WORKER_PID"

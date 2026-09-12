#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

PM_SPEC="$(node -p "require('./package.json').packageManager || 'pnpm@10.27.0'")"
corepack enable
corepack prepare "$PM_SPEC" --activate

if [[ ! -d node_modules ]]; then
  pnpm install --frozen-lockfile
fi

cleanup() {
  jobs -p | xargs -r kill 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Prefer the repository's pinned E2E infrastructure. It brings up Anvil,
# Alto, a mock paymaster, mock orchestrator, Panoptes, and DQA services.
pnpm --filter @ens-apps/e2e infra:up

# Start all packages that actually expose a dev script. Using --if-present
# avoids the invalid assumption that every app/worker has one.
pnpm --parallel --stream --if-present \
  --filter './apps/*' \
  --filter './workers/*' \
  dev &
DEV_PID=$!

cat <<'EOF'

ENS audit development stack started.
- Local Sepolia fork: http://127.0.0.1:8545
- ERC-4337 bundler:   http://127.0.0.1:4337
- Mock orchestrator:  http://127.0.0.1:3007
- DQA service:        http://127.0.0.1:4000

App ports are printed by the individual Vite/Wrangler processes.
Press Ctrl+C to stop the foreground dev processes. Run
  pnpm --filter @ens-apps/e2e infra:down
to tear down the Docker E2E infrastructure.
EOF

wait "$DEV_PID"

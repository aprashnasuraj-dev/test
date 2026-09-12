#!/usr/bin/env bash
set -Eeuo pipefail

UPSTREAM_REPO="${UPSTREAM_REPO:-https://github.com/immunefi-team/audit-comp-ens.git}"
UPSTREAM_REF="${UPSTREAM_REF:-1c9b47f18fcddd2e864dfe385c4171061c9811ae}"
WORKSPACE_DIR="${WORKSPACE_DIR:-ens-workspace}"
PNPM_VERSION="${PNPM_VERSION:-10.27.0}"
NODE_MAJOR="${NODE_MAJOR:-20}"

log() { printf '\n==> %s\n' "$*"; }
need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing required command: $1" >&2; exit 1; }; }

need git
need curl

if ! command -v nvm >/dev/null 2>&1; then
  export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
  if [[ -s "$NVM_DIR/nvm.sh" ]]; then
    # shellcheck source=/dev/null
    . "$NVM_DIR/nvm.sh"
  else
    log "Installing NVM"
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    # shellcheck source=/dev/null
    . "$NVM_DIR/nvm.sh"
  fi
fi

log "Installing/activating Node ${NODE_MAJOR}"
nvm install "$NODE_MAJOR"
nvm use "$NODE_MAJOR"
nvm alias default "$NODE_MAJOR"

log "Activating pnpm ${PNPM_VERSION}"
corepack enable
corepack prepare "pnpm@${PNPM_VERSION}" --activate

if ! command -v rustup >/dev/null 2>&1; then
  log "Installing Rust toolchain"
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
  # shellcheck source=/dev/null
  . "$HOME/.cargo/env"
fi
rustup toolchain install stable
rustup default stable

if ! command -v foundryup >/dev/null 2>&1; then
  log "Installing Foundry bootstrap"
  curl -fsSL https://foundry.paradigm.xyz | bash
  export PATH="$HOME/.foundry/bin:$PATH"
fi
foundryup

if ! command -v semgrep >/dev/null 2>&1; then
  log "Installing Semgrep"
  if command -v pipx >/dev/null 2>&1; then
    pipx install semgrep
  else
    python3 -m pip install --user semgrep
    export PATH="$HOME/.local/bin:$PATH"
  fi
fi

if [[ ! -d "$WORKSPACE_DIR/.git" ]]; then
  log "Cloning upstream ENS workspace"
  git clone --branch audit-comp-ready --single-branch "$UPSTREAM_REPO" "$WORKSPACE_DIR"
fi

log "Pinning audited upstream commit ${UPSTREAM_REF}"
git -C "$WORKSPACE_DIR" fetch origin audit-comp-ready
git -C "$WORKSPACE_DIR" checkout --detach "$UPSTREAM_REF"

log "Installing upstream dependencies"
(
  cd "$WORKSPACE_DIR"
  pnpm install --frozen-lockfile
  cp apps/manager/.env.example apps/manager/.env.local 2>/dev/null || touch apps/manager/.env.local
  cp apps/portal/.env.example apps/portal/.env.local 2>/dev/null || touch apps/portal/.env.local
  pnpm --filter @ens-apps/smart-account typecheck
  pnpm --filter @ens-apps/transaction-manager typecheck
)

log "Installing custom audit tooling"
(
  cd tooling
  pnpm install
  pnpm check
)

log "Environment ready"
printf 'Node:     %s\n' "$(node --version)"
printf 'pnpm:     %s\n' "$(pnpm --version)"
printf 'Rust:     %s\n' "$(rustc --version)"
printf 'Foundry:  %s\n' "$(forge --version | head -n1)"
printf 'Anvil:    %s\n' "$(anvil --version | head -n1)"
printf 'Semgrep:  %s\n' "$(semgrep --version | head -n1)"
printf 'Upstream: %s\n' "$(git -C "$WORKSPACE_DIR" rev-parse HEAD)"

echo
echo "Upstream E2E stack: cd $WORKSPACE_DIR && pnpm e2e:infra:up"
echo "Manager:            cd $WORKSPACE_DIR && pnpm dev:manager"
echo "API worker:         cd $WORKSPACE_DIR && pnpm --filter api-worker dev"

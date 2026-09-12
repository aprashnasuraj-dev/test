#!/usr/bin/env bash
set -Eeuo pipefail

UPSTREAM_REPO="${UPSTREAM_REPO:-https://github.com/immunefi-team/audit-comp-ens.git}"
UPSTREAM_REF="${UPSTREAM_REF:-1c9b47f18fcddd2e864dfe385c4171061c9811ae}"
WORKSPACE_DIR="${WORKSPACE_DIR:-ens-workspace}"
PNPM_VERSION="${PNPM_VERSION:-10.27.0}"
CORE_NODE_VERSION="${CORE_NODE_VERSION:-20}"
FULL_NODE_VERSION="${FULL_NODE_VERSION:-22.18.0}"
FOUNDRY_VERSION="${FOUNDRY_VERSION:-1.7.1}"
SEMGREP_VERSION="${SEMGREP_VERSION:-1.177.0}"

log() { printf '\n==> %s\n' "$*"; }
need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing required command: $1" >&2; exit 1; }; }
activate_pnpm() {
  corepack enable
  corepack prepare "pnpm@${PNPM_VERSION}" --activate
  test "$(pnpm --version)" = "$PNPM_VERSION"
}

need git
need curl
need python3

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [[ ! -s "$NVM_DIR/nvm.sh" ]]; then
  log "Installing NVM 0.39.7"
  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
fi
# shellcheck source=/dev/null
. "$NVM_DIR/nvm.sh"

log "Installing Node ${CORE_NODE_VERSION} core-audit lane"
nvm install "$CORE_NODE_VERSION"
nvm use "$CORE_NODE_VERSION"
activate_pnpm

if ! command -v rustup >/dev/null 2>&1; then
  log "Installing Rust toolchain"
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
fi
# shellcheck source=/dev/null
[[ -s "$HOME/.cargo/env" ]] && . "$HOME/.cargo/env"
rustup toolchain install stable
rustup default stable

if ! command -v foundryup >/dev/null 2>&1; then
  log "Installing Foundry bootstrap"
  curl -fsSL https://foundry.paradigm.xyz | bash
fi
export PATH="$HOME/.foundry/bin:$HOME/.local/bin:$PATH"
log "Installing Foundry ${FOUNDRY_VERSION}"
foundryup --install "$FOUNDRY_VERSION"

if ! command -v semgrep >/dev/null 2>&1 || [[ "$(semgrep --version 2>/dev/null | head -n1)" != "$SEMGREP_VERSION" ]]; then
  log "Installing Semgrep ${SEMGREP_VERSION}"
  if command -v pipx >/dev/null 2>&1; then
    pipx install --force "semgrep==${SEMGREP_VERSION}"
  else
    python3 -m pip install --user --upgrade "semgrep==${SEMGREP_VERSION}"
  fi
fi

if [[ ! -d "$WORKSPACE_DIR/.git" ]]; then
  log "Cloning upstream ENS workspace"
  git clone --branch audit-comp-ready --single-branch "$UPSTREAM_REPO" "$WORKSPACE_DIR"
fi

log "Pinning audited upstream commit ${UPSTREAM_REF}"
git -C "$WORKSPACE_DIR" fetch origin audit-comp-ready
git -C "$WORKSPACE_DIR" checkout --detach "$UPSTREAM_REF"
test "$(git -C "$WORKSPACE_DIR" rev-parse HEAD)" = "$UPSTREAM_REF"

log "Installing upstream dependencies under Node ${CORE_NODE_VERSION}"
(
  cd "$WORKSPACE_DIR"
  pnpm install --frozen-lockfile
  cp apps/manager/.env.example apps/manager/.env.local 2>/dev/null || touch apps/manager/.env.local
  cp apps/portal/.env.example apps/portal/.env.local 2>/dev/null || touch apps/portal/.env.local
  pnpm --filter @ens-apps/smart-account typecheck
  pnpm --filter @ens-apps/transaction-manager typecheck
  pnpm --filter @ens-apps/smart-account test
  pnpm --filter @ens-apps/transaction-manager test
)

log "Switching to Node ${FULL_NODE_VERSION} for the full ENS application stack"
nvm install "$FULL_NODE_VERSION"
nvm use "$FULL_NODE_VERSION"
nvm alias default "$FULL_NODE_VERSION"
activate_pnpm
node -e "const [maj,min]=process.versions.node.split('.').map(Number); if (maj < 22 || (maj === 22 && min < 18)) process.exit(1)"

log "Building Manager, Portal, and API worker"
(
  cd "$WORKSPACE_DIR"
  pnpm build:manager
  pnpm build:portal
  pnpm --filter api-worker build
  pnpm --filter @ens-apps/e2e exec playwright install --with-deps chromium
)

log "Installing and testing custom audit tooling"
(
  cd tooling
  pnpm install --frozen-lockfile=false
  pnpm check
)

log "Validating custom Semgrep rules"
semgrep scan --validate --config tooling/ast-rules/ens-security.yml

log "Environment ready"
printf 'Core Node lane: %s\n' "$CORE_NODE_VERSION"
printf 'Full Node:      %s\n' "$(node --version)"
printf 'pnpm:           %s\n' "$(pnpm --version)"
printf 'Rust:           %s\n' "$(rustc --version)"
printf 'Foundry:        %s\n' "$(forge --version | head -n1)"
printf 'Anvil:          %s\n' "$(anvil --version | head -n1)"
printf 'Semgrep:        %s\n' "$(semgrep --version | head -n1)"
printf 'Upstream:       %s\n' "$(git -C "$WORKSPACE_DIR" rev-parse HEAD)"

echo
echo "E2E infrastructure: cd $WORKSPACE_DIR && pnpm e2e:infra:up"
echo "Manager:            cd $WORKSPACE_DIR && pnpm dev:manager"
echo "Portal:             cd $WORKSPACE_DIR/apps/portal && pnpm dev"
echo "API worker:         cd $WORKSPACE_DIR && pnpm --filter api-worker dev"
echo "UserOp corpus:      pnpm --dir tooling mutate:userop"
echo "ENS stress corpus:  pnpm --dir tooling stress:ens"
echo "State hydrator:     pnpm --dir tooling hydrate"

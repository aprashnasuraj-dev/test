#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This installer is intended for Ubuntu/Linux or WSL2." >&2
  exit 2
fi

export DEBIAN_FRONTEND=noninteractive
sudo apt-get update
sudo apt-get install -y \
  ca-certificates curl git jq tar gzip build-essential \
  python3 python3-pip python3-venv pipx z3

python3 -m pipx ensurepath >/dev/null 2>&1 || true
export PATH="$HOME/.local/bin:$HOME/.foundry/bin:$HOME/.cargo/bin:$PATH"

install_pipx_tool() {
  local package="$1"
  local binary="$2"
  if command -v "$binary" >/dev/null 2>&1; then
    echo "$binary already installed: $($binary --version 2>/dev/null | head -n1 || true)"
    return
  fi
  pipx install "$package"
}

install_pipx_tool "semgrep" "semgrep"
install_pipx_tool "slither-analyzer" "slither"
install_pipx_tool "bandit" "bandit"
install_pipx_tool "pip-audit" "pip-audit"
install_pipx_tool "detect-secrets" "detect-secrets"

if ! command -v myth >/dev/null 2>&1; then
  if command -v python3.10 >/dev/null 2>&1; then
    pipx install --python "$(command -v python3.10)" mythril
  else
    echo "Mythril skipped: upstream PyPI guidance supports Python 3.7-3.10 and python3.10 is not installed." >&2
    echo "Install a Python 3.10 interpreter in WSL, then run: pipx install --python python3.10 mythril" >&2
  fi
fi

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi
if ! command -v halmos >/dev/null 2>&1; then
  uv tool install --python 3.12 halmos
fi

if ! command -v forge >/dev/null 2>&1; then
  curl -L https://foundry.paradigm.xyz | bash
  export PATH="$HOME/.foundry/bin:$PATH"
  "$HOME/.foundry/bin/foundryup"
fi

if ! command -v echidna >/dev/null 2>&1; then
  tmp_dir="$(mktemp -d)"
  trap 'rm -rf "$tmp_dir"' EXIT
  release_json="$tmp_dir/echidna-release.json"
  curl -fsSL \
    -H 'Accept: application/vnd.github+json' \
    -H 'User-Agent: ENS-Audit-Runner-Installer' \
    https://api.github.com/repos/crytic/echidna/releases/latest \
    -o "$release_json"

  mapfile -t asset_fields < <(
    python3 - "$release_json" <<'PY'
import json
import re
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assets = [
    item for item in payload.get("assets", [])
    if re.fullmatch(r"echidna-[0-9.]+-x86_64-linux\.tar\.gz", str(item.get("name", "")))
]
if len(assets) != 1:
    raise SystemExit(f"expected one x86_64 Linux Echidna asset, found {len(assets)}")
asset = assets[0]
print(asset["name"])
print(asset["browser_download_url"])
print(asset.get("digest") or "")
PY
  )

  asset_name="${asset_fields[0]}"
  asset_url="${asset_fields[1]}"
  asset_digest="${asset_fields[2]}"
  archive="$tmp_dir/$asset_name"
  curl -fL "$asset_url" -o "$archive"

  if [[ "$asset_digest" == sha256:* ]]; then
    expected="${asset_digest#sha256:}"
    actual="$(sha256sum "$archive" | awk '{print $1}')"
    if [[ "$actual" != "$expected" ]]; then
      echo "Echidna SHA-256 verification failed." >&2
      exit 3
    fi
  fi

  mkdir -p "$HOME/.local/bin"
  tar -xzf "$archive" -C "$tmp_dir"
  echidna_path="$(find "$tmp_dir" -type f -name echidna -perm -u+x | head -n1)"
  if [[ -z "$echidna_path" ]]; then
    echo "Echidna archive extracted but executable was not found." >&2
    exit 4
  fi
  install -m 0755 "$echidna_path" "$HOME/.local/bin/echidna"
fi

if command -v npm >/dev/null 2>&1 && ! command -v snyk >/dev/null 2>&1; then
  echo "Optional Snyk CLI is not installed. Official npm install command: npm install -g snyk"
fi

cat <<'EOF'

WSL analyzer setup complete.
Ensure this line is present in your shell profile if a new terminal cannot find the tools:
  export PATH="$HOME/.local/bin:$HOME/.foundry/bin:$HOME/.cargo/bin:$PATH"

Installed/verified commands:
EOF

for command_name in semgrep slither bandit myth halmos forge echidna pip-audit detect-secrets; do
  if command -v "$command_name" >/dev/null 2>&1; then
    printf '  %-16s %s\n' "$command_name" "$(command -v "$command_name")"
  else
    printf '  %-16s %s\n' "$command_name" "MISSING"
  fi
done

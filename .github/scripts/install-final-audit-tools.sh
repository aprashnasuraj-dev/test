#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "final audit tool installer requires Linux" >&2
  exit 2
fi

export DEBIAN_FRONTEND=noninteractive
export PATH="$HOME/.local/bin:$HOME/.foundry/bin:$HOME/.config/.foundry/bin:$HOME/.cargo/bin:$PATH"
mkdir -p "$HOME/.local/bin" "$HOME/.local/share/ens-audit-tools"

echo "$HOME/.local/bin" >> "${GITHUB_PATH:-/dev/null}"
echo "$HOME/.foundry/bin" >> "${GITHUB_PATH:-/dev/null}"
echo "$HOME/.config/.foundry/bin" >> "${GITHUB_PATH:-/dev/null}"
echo "$HOME/.cargo/bin" >> "${GITHUB_PATH:-/dev/null}"

sudo apt-get update
sudo apt-get install -y ca-certificates curl jq unzip tar gzip build-essential z3
python -m pip install --upgrade pip pipx uv

install_pipx_tool() {
  local package="$1"
  local binary="$2"
  if command -v "$binary" >/dev/null 2>&1; then
    return
  fi
  pipx install "$package"
}

release_asset_fields() {
  local repository="$1"
  local name_regex="$2"
  local json_file="$3"
  local curl_args=(
    -fsSL
    -H 'Accept: application/vnd.github+json'
    -H 'User-Agent: ENS-Audit-Runner-Final'
  )
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    curl_args+=( -H "Authorization: Bearer ${GITHUB_TOKEN}" )
  fi
  curl "${curl_args[@]}" \
    "https://api.github.com/repos/${repository}/releases/latest" \
    -o "$json_file"
  python - "$json_file" "$name_regex" <<'PY'
import json
import re
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
pattern = re.compile(sys.argv[2])
assets = [item for item in payload.get("assets", []) if pattern.fullmatch(str(item.get("name", "")))]
if len(assets) != 1:
    raise SystemExit(f"expected one release asset matching {pattern.pattern!r}; found {len(assets)}")
asset = assets[0]
print(asset["name"])
print(asset["browser_download_url"])
print(asset.get("digest") or "")
PY
}

download_release_asset() {
  local repository="$1"
  local name_regex="$2"
  local destination="$3"
  local metadata="$4"
  mapfile -t asset < <(release_asset_fields "$repository" "$name_regex" "$metadata")
  curl -fL "${asset[1]}" -o "$destination"
  if [[ "${asset[2]}" == sha256:* ]]; then
    local expected="${asset[2]#sha256:}"
    local actual
    actual="$(sha256sum "$destination" | awk '{print $1}')"
    if [[ "$actual" != "$expected" ]]; then
      echo "SHA-256 verification failed for ${asset[0]}." >&2
      exit 4
    fi
  fi
}

install_archive_binary() {
  local repository="$1"
  local name_regex="$2"
  local binary="$3"
  local archive_type="$4"
  if command -v "$binary" >/dev/null 2>&1; then
    return
  fi
  local temp_dir
  temp_dir="$(mktemp -d)"
  local archive="$temp_dir/archive"
  download_release_asset "$repository" "$name_regex" "$archive" "$temp_dir/release.json"
  local extract_dir="$temp_dir/extract"
  mkdir -p "$extract_dir"
  if [[ "$archive_type" == "zip" ]]; then
    unzip -q "$archive" -d "$extract_dir"
  else
    tar -xzf "$archive" -C "$extract_dir"
  fi
  local binary_path
  binary_path="$(find "$extract_dir" -type f -name "$binary" -perm -u+x | head -n1)"
  if [[ -z "$binary_path" ]]; then
    echo "$binary was not found in downloaded release archive" >&2
    exit 5
  fi
  local install_root="$HOME/.local/share/ens-audit-tools/$binary"
  rm -rf "$install_root"
  mkdir -p "$install_root"
  cp -a "$extract_dir"/. "$install_root"/
  binary_path="$(find "$install_root" -type f -name "$binary" -perm -u+x | head -n1)"
  ln -sfn "$binary_path" "$HOME/.local/bin/$binary"
  rm -rf "$temp_dir"
}

if [[ "${ACCEPT_CODEQL_TERMS:-false}" == "true" ]]; then
  install_archive_binary \
    "github/codeql-cli-binaries" '^codeql-linux64\.zip$' "codeql" "zip"
else
  echo "SKIP codeql: CodeQL terms were not explicitly accepted for this run."
fi

install_archive_binary \
  "trufflesecurity/trufflehog" '^trufflehog_[0-9.]+_linux_amd64\.tar\.gz$' "trufflehog" "tar"
install_archive_binary \
  "crytic/echidna" '^echidna-[0-9.]+-x86_64-linux\.tar\.gz$' "echidna" "tar"

install_pipx_tool "semgrep" "semgrep"
install_pipx_tool "slither-analyzer" "slither"
install_pipx_tool "detect-secrets" "detect-secrets"

if ! command -v myth >/dev/null 2>&1; then
  uv python install 3.10
  uv tool install --python 3.10 mythril
fi
if ! command -v halmos >/dev/null 2>&1; then
  uv tool install --python 3.12 halmos
fi

if ! command -v forge >/dev/null 2>&1; then
  temp_dir="$(mktemp -d)"
  curl -fL https://foundry.paradigm.xyz -o "$temp_dir/foundryup.sh"
  bash "$temp_dir/foundryup.sh"
  rm -rf "$temp_dir"

  for foundry_dir in "$HOME/.foundry/bin" "$HOME/.config/.foundry/bin"; do
    if [[ -x "$foundry_dir/foundryup" ]]; then
      export PATH="$foundry_dir:$PATH"
      echo "$foundry_dir" >> "${GITHUB_PATH:-/dev/null}"
      break
    fi
  done

  if ! command -v foundryup >/dev/null 2>&1; then
    echo "foundryup installer completed but foundryup was not found in a supported install path" >&2
    exit 6
  fi
  foundryup
fi

if [[ -n "${SNYK_TOKEN:-}" ]] && ! command -v snyk >/dev/null 2>&1; then
  npm install -g snyk
elif [[ -z "${SNYK_TOKEN:-}" ]]; then
  echo "SKIP snyk: SNYK_TOKEN is not configured."
fi

printf '%s\n' "External analyzer tool installation completed."

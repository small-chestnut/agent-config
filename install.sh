#!/usr/bin/env bash
# Install agent config templates to the user's home directory (Linux / macOS / WSL2).
# Also runs automatically when this repo is set as a Codespaces dotfiles repository.
set -euo pipefail
repo="$(cd "$(dirname "$0")" && pwd)"

install_file() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [ -f "$dst" ]; then
    if cmp -s "$src" "$dst"; then
      echo "  unchanged: $dst"
      return
    fi
    if [ ! -t 0 ]; then
      # Non-interactive (e.g. Codespaces provisioning): keep the existing file.
      echo "  non-interactive, keeping existing: $dst"
      return
    fi
    echo "--- existing file differs: $dst ---"
    diff -u "$dst" "$src" || true
    read -r -p "  overwrite? (y/N) " ans
    if [ "${ans}" != "y" ]; then
      echo "  skipped: $dst"
      return
    fi
  fi
  cp "$src" "$dst"
  echo "  installed: $dst"
}

echo "Installing Claude Code settings..."
install_file "$repo/claude/user-settings.json" "$HOME/.claude/settings.json"

# NOTE: ~/.codex/config.toml is managed by the Codex app itself (plugins, trusted
# projects, MCP servers). Never copy over it. Apply codex/safety-snippet.toml by hand.
echo "Installing Codex CLI profile (config.toml is NOT touched)..."
install_file "$repo/codex/readonly.config.toml" "$HOME/.codex/readonly.config.toml"

echo "Done. Restart agent sessions for changes to take effect."

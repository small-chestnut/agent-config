#!/usr/bin/env bash
# Install agent config templates to the user's home directory (Linux / macOS / WSL2).
# Also runs automatically when this repo is set as a Codespaces dotfiles repository.
# Usage: ./install.sh [--yes]   (--yes overwrites differing files without asking)
set -euo pipefail
repo="$(cd "$(dirname "$0")" && pwd)"
yes=0
[ "${1:-}" = "--yes" ] && yes=1

install_file() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [ -f "$dst" ]; then
    if cmp -s "$src" "$dst"; then
      echo "  unchanged: $dst"
      return
    fi
    if [ "$yes" = 1 ]; then
      cp "$src" "$dst"
      echo "  overwritten: $dst"
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
# Claude Code reads settings.json, CLAUDE.md and skills/ from the directory named by
# CLAUDE_CONFIG_DIR, defaulting to ~/.claude. A second account (a separate login under a
# separate CLAUDE_CONFIG_DIR) therefore reads a different copy of both files, and gets no
# safety settings at all unless they are installed there too.
claude_dirs=("$HOME/.claude")
# Extra config dirs are opt-in per machine: listed here, but only used when the directory
# already exists. Create the directory to start managing it; machines without it are
# unaffected.
for extra in "$HOME/.claude-work"; do
  if [ -d "$extra" ]; then
    claude_dirs+=("$extra")
  fi
done
for dir in "${claude_dirs[@]}"; do
  install_file "$repo/claude/user-settings.json" "$dir/settings.json"
  install_file "$repo/claude/CLAUDE.md" "$dir/CLAUDE.md"
done

# Skills: one folder per skill, SKILL.md inside. The body is loaded only when the
# skill is invoked, so procedures live here instead of bloating CLAUDE.md. Installed
# into every config dir, like CLAUDE.md.
echo "Installing Claude Code skills..."
for d in "$repo"/claude/skills/*/; do
  [ -f "${d}SKILL.md" ] || continue
  for dir in "${claude_dirs[@]}"; do
    install_file "${d}SKILL.md" "$dir/skills/$(basename "$d")/SKILL.md"
  done
done

# Hooks: scripts that settings.json runs on tool events (see "hooks" in user-settings.json).
# Installed into every config dir; the hook command finds them via CLAUDE_CONFIG_DIR.
echo "Installing Claude Code hooks..."
for f in "$repo"/claude/hooks/*; do
  [ -f "$f" ] || continue
  for dir in "${claude_dirs[@]}"; do
    install_file "$f" "$dir/hooks/$(basename "$f")"
  done
done

# NOTE: ~/.codex/config.toml is managed by the Codex app itself (plugins, trusted
# projects, MCP servers). Never copy over it. Apply codex/safety-snippet.toml by hand.
echo "Installing Codex CLI profile (config.toml is NOT touched)..."
install_file "$repo/codex/readonly.config.toml" "$HOME/.codex/readonly.config.toml"
install_file "$repo/codex/AGENTS.md" "$HOME/.codex/AGENTS.md"

echo "Checking for a trash command (agents use it instead of rm; see claude/CLAUDE.md)..."
if command -v trash >/dev/null 2>&1 || command -v trash-put >/dev/null 2>&1; then
  echo "  trash: found"
else
  echo "  trash: NOT found. Recommended: 'sudo apt install trash-cli' (Linux) or 'brew install trash' (macOS)."
  echo "  Until installed, agents fall back to moving files into ~/.agent-trash/."
fi

echo "Done. Restart agent sessions for changes to take effect."

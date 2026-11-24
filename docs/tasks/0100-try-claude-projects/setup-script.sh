#!/bin/bash
# クラウドの環境のセットアップスクリプト。agent-config をインストールし、経過を記録に残す。
# 失敗してもスレッドが始まるように、最後は必ず 0 で終わる。
src="${TRIAL_SRC:-/opt/agent-config}"
log="${TRIAL_LOG:-/var/log/agent-config-setup.log}"
{
  echo "user=$(id -un) HOME=$HOME pwd=$PWD CLAUDE_CONFIG_DIR=${CLAUDE_CONFIG_DIR:-none}"
  echo "before:"; ls -la "$HOME/.claude"
  if git clone -q --depth 1 https://github.com/small-chestnut/agent-config.git "$src"; then
    echo "fetch=git"
  else
    mkdir -p "$src"
    curl -fsSL https://github.com/small-chestnut/agent-config/archive/refs/heads/main.tar.gz \
      | tar xz -C "$src" --strip-components=1 && echo "fetch=tarball" || echo "fetch=failed"
  fi
  bash "$src/install.sh" --yes; echo "install exit=$?"
  echo "after:"; ls -la "$HOME/.claude"
} > "$log" 2>&1
exit 0

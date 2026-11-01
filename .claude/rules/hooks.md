---
paths:
  - claude/hooks/*.py
---

# 原則1: 強制

## 目的: 例外の無い決まりを、モデルの判断で破らせない

### 目指す状態: 「短く」と書くだけでは通る長い決まりの行を、フックが止めている

- `check_rule_length.py` を、文書の規則に置き換えていない。

### 目指す状態: 書いている最中には気づけない冗長さに、1か所を指して問い返している

- `ask_removable_words.py` は、足した行を1か所ずつ指して問い返している。

### 目指す状態: Bash や PowerShell で書いた決まりの文書も、素通りしていない

- `check_rule_documents_changed_by_shell.py` が、シェルで書いた行にも同じ2つを掛けている。
- コマンドに出ないパスへ書くスクリプトは、cwd のリポジトリの分だけ見えている。

### 目指す状態: モデルの判断で、確かめずにターンを終えない

- `require_verify_before_stop.py` を、CLAUDE.md の規則に置き換えていない。
- ツールを使わずに8回続けて止めると、Claude Code がターンを終わらせる。

### 目指す状態: 文字列のパターンで書けない履歴を消す push も、止まっている

- `block_history_erasing_push.py` を、deny のパターンに置き換えていない。

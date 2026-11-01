ステータス: 実装中

# ゴール

agent-config から Codex 用の設定が無くなり、install しても `~/.codex/` に何も配置されない。利用者の環境に入っている、agent-config が配置した Codex のファイルも片づいている。

利用者の理由: Codex 用の設定は更新していないので、消す。

範囲外: `docs/tasks/` の過去の記録・採用済みの ADR の本文・フック `check_rule_length.py` が数える AGENTS.md・`~/.codex/config.toml`。

# 受け入れ条件

1. リポジトリに `codex/` フォルダが無い。
2. `install.ps1` と `install.sh` に Codex の部分が無く、どちらも構文エラーが無い。
3. README に、`docs/tasks/` の外の Codex の記述が無い。
4. README で AGENTS.md が出てくるのは、作業するリポジトリの文書としての AGENTS.md(リポジトリの決まりの例)と、フック `check_rule_length.py` の説明だけ。
5. `python -m unittest discover -s tests` が通る。
6. マージと install のあと、利用者の `~/.codex/AGENTS.md` と `~/.codex/readonly.config.toml` が `~/.agent-trash/` にあり、`~/.codex/config.toml` は手を付ける前と同じ中身。

# 設計

文書と設定だけの変更で、ADR に残す決定は無い。README の行 171 に付いた ADR 0004-1 は、agent-config の規則がリポジトリの決まりに負けるという決定で、AGENTS.md が無くなっても変わらないので、ADR の本文は変えない。新しい名前は無いので、用語集は変えない。

## 手順1: `codex/` を消す(PG)

- `codex/AGENTS.md`・`codex/readonly.config.toml`・`codex/safety-snippet.toml` を `git rm` で消す。

## 手順2: install スクリプトから Codex の部分を外す(PG)

- `install.ps1`: 「# NOTE: ~/.codex/config.toml is managed by the Codex app itself」から `Install-ConfigFile "$repo\codex\AGENTS.md" ...` までの5行と、その下の空行を消す。
- `install.sh`: 「# NOTE: ~/.codex/config.toml is managed by the Codex app itself」から `install_file "$repo/codex/AGENTS.md" ...` までの5行と、その下の空行を消す。

## 手順3: README から Codex の記述を外す(PG)

- 冒頭の「AI コーディングエージェント(Claude Code / Codex CLI)の設定として」を「Claude Code の設定として」にする。
- 「全プロジェクト共通の指示(`CLAUDE.md`・`AGENTS.md`)」を「全プロジェクト共通の指示(`CLAUDE.md`)」にする。
- 「構成」の木から、`codex/` とその下の3行を消す。
- 「## Codex CLI テンプレートの意図」の節を、見出しから次の見出しの前まで消す。
- 見出し「## プロンプト層(CLAUDE.md / AGENTS.md)の意図」を「## プロンプト層(CLAUDE.md)の意図」にする。
- その節の最初の文の「CLAUDE.md /\nAGENTS.md は」を「CLAUDE.md は」にする。
- 「各リポジトリ直下に `CLAUDE.md` / `AGENTS.md` を」を「各リポジトリ直下に `CLAUDE.md` を」にする。
- 「作業するリポジトリの決まりは、agent-config の規則に勝つ」の行の「CLAUDE.md の冒頭と AGENTS.md の最初の節に書く。」を「CLAUDE.md の冒頭に書く。」にする。
- 「セッションの役割分割」の節の「**QA を Codex にする案は保留**」の項目(3行)を消す。
- 次の2か所は、作業するリポジトリの AGENTS.md とフックの話なので残す: 「コミットされた文書(CLAUDE.md・AGENTS.md・README・…)」と、`hooks/check_rule_length.py` の「名前が CLAUDE.md・AGENTS.md・SKILL.md の」。

## 手順4: 利用者の環境の Codex のファイルを移す(PL・マージの後)

- `~/.codex/AGENTS.md` と `~/.codex/readonly.config.toml` を `~/.agent-trash/` へ `mv` で移す。`mv` なので、戻すときは移し返せる。
- `~/.codex/config.toml` には触らない。Codex 本体が状態を書き込むファイルで、agent-config が配置したものではないため。
- 移す前と後で `~/.codex/config.toml` のハッシュを比べる。
- install(`install.ps1 -Yes`)は、手順1〜3を main に入れたあとで走らせる。前に走らせると、消したファイルがまた配置される。

## テスト一覧

文書と設定だけの変更なので、テストは作らない。確かめ方を並べる。

| 確かめ方 | する人 | 受け入れ条件 |
|---|---|---|
| `git ls-files codex` が何も出さない | PG | 1 |
| `bash -n install.sh` と、PowerShell の `[System.Management.Automation.Language.Parser]::ParseFile` で `install.ps1` を読み、エラーが0個 | PG | 2 |
| `git grep -i -n codex -- . ':!docs/tasks'` が何も出さない | PG | 1・2・3 |
| `git grep -n AGENTS.md -- README.md` の結果が、手順3で残すと書いた2か所だけ | PG | 4 |
| `python -m unittest discover -s tests` | PG | 5 |
| `~/.agent-trash/` に2つのファイルがあり、`~/.codex/config.toml` のハッシュが移す前と同じ | PL | 6 |

# 実装

# レビュー

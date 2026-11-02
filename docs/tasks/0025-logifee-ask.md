ステータス: 実装レビュー済み

# ゴール

この PC の Claude Code で、LogiFee の MCP サーバが本番(七海 `logifee-nnm`・SD `logifee-sd`)に書くツール `execute_plan` は、呼ぶたびに利用者に確かめを訊く。そうするユーザー設定が、agent-config の main と、この PC の Claude 設定ディレクトリに入っている。

範囲外: MCP サーバの登録(`claude mcp add … --scope user`・`LOGIFEE_ALLOW_WRITE=1`)と、`execute_plan` のほかの LogiFee のツールの permissions。

# 受け入れ条件

1. `claude/user-settings.json` の `permissions.ask` に、`mcp__logifee-nnm__execute_plan` と `mcp__logifee-sd__execute_plan` がある。
2. `claude/user-settings.json` は JSON として読め、1 の2行のほかは変える前と同じである。
3. `.claude/rules/settings.md` に、`execute_plan` を ask にし、deny にしない理由(開発者が本番に書けないと困る)の行がある。
4. `.claude/rules/settings.md` に、`execute_plan` を allow にしない理由(LogiFee の `LogiFeeMCP/README.md` が毎回訊かせると決めている)の行がある。
5. `.claude/rules/settings.md` の、3・4 の2行のほかは変える前と同じである。
6. `python -m unittest discover -s tests` が全部通る。
7. main に入れて `install.ps1 -Yes` を走らせたあと、`~/.claude/settings.json` の `permissions.ask` に、1 の2つがある。

# 設計

設定と、その「なぜ」の文書だけの変更。`claude/user-settings.json` は skill でも hooks のファイルでもなく、このリポジトリのモジュールに当たらないので、仕様は作らない。書き換える2つのファイルに ADR の番号は無い。足す行には ADR を付けない。

規則の書き方: MCP のツール1つは `mcp__<サーバ>__<ツール>` と書く。サーバ名の `-` はそのまま。ask は allow より先に効く(https://code.claude.com/docs/en/permissions)。

## 手順

| 番号 | する人 | すること |
|---|---|---|
| 1 | PG | `claude/user-settings.json` の `permissions.ask` の配列の末尾(`"PowerShell(git restore *)"` の次)に、`"mcp__logifee-nnm__execute_plan"`・`"mcp__logifee-sd__execute_plan"` をこの順に足す。前の行の末尾に `,` を足す |
| 2 | PG | `.claude/rules/settings.md` の「### 目指す状態: 操作は、戻せるかどうかで3色に分かれている」の最後の行(`- 履歴の書き換えは …`)の次に、下の2行を足す |
| 3 | PG | 確かめ: `python -c "import json; d=json.load(open('claude/user-settings.json', encoding='utf-8')); print(d['permissions']['ask'])"` で1の2つが出る。`git diff` が1・2の行だけ。`python -m unittest discover -s tests` が通る |
| 4 | PG | コミットする。本文に利用者の「なぜ」を書く: この PC の Claude Code で LogiFee の MCP サーバが使えるので入れておく。開発者が本番に書けないと困るので、本番に書くツールも出す形で使う |
| 5 | PL | main にマージし、push し、agent-config の main のチェックアウトで `install.ps1 -Yes` を走らせる。`~/.claude/settings.json` の `permissions.ask` に1の2つがあるのを確かめる |

手順2で足す2行(どちらも60字以内):

```
- LogiFee の本番に書く `execute_plan` は ask。開発者が本番に書けないと困るので deny にしない。
- `execute_plan` を allow にしない。LogiFee の `LogiFeeMCP/README.md` が、毎回訊かせると決めている。
```

手順5の補足: `install.ps1 -Yes` は差分を見せずに `~/.claude/settings.json` を上書きする。設計の時点で、`~/.claude/settings.json` と `claude/user-settings.json` の中身は同じだった。`~/.claude-work` はこの PC に無い。

## テスト一覧

設定と文書だけの変更なので、テストを作らない。

| 確かめ方 | 大きさ | 受け入れ条件 |
|---|---|---|
| 手順3の `python -c …` の出力に2つがある | — | 1・2 |
| 手順3の `git diff` が、`claude/user-settings.json` の2行と `,`、`.claude/rules/settings.md` の2行だけ | — | 2・3・4・5 |
| `python -m unittest discover -s tests` | 既存 | 6 |
| 手順5のあと、`~/.claude/settings.json` を手順3と同じ `python -c …` で読む | — | 7 |

# 実装

手順1〜4をした。設計から変えた所は無い。

- `claude/user-settings.json` の `permissions.ask` の末尾に `mcp__logifee-nnm__execute_plan`・`mcp__logifee-sd__execute_plan` を足した。
- `.claude/rules/settings.md` に、ask にして deny にしない理由と、allow にしない理由の2行を足した。
- `python -c "import json; …"` で `permissions.ask` の末尾3つに2つがあるのを確かめた(JSON として読める)。
- `git diff` は、user-settings.json の2行と `,`、settings.md の2行だけ。
- `python -m unittest discover -s tests`: 64 件 OK。
- テストと lint は、設計のテスト一覧のとおり新しく作っていない。

# レビュー

指摘なし

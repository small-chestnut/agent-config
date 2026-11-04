ステータス: 実装レビュー中

# ゴール

`claude/hooks/require_verify_before_stop.py` の 130 行目のコメントが、`shutil.copy2` が更新時刻ごとコピーすることを、IT の用語「保持」で言っている。全体の CLAUDE.md の原則3「言葉は、広く使われている呼び名で書いている。IT の用語があれば、その用語。」に沿わせるため。

範囲外: このフックのほかの行と、ほかのファイルの言い換え。フックの動き。

# 受け入れ条件

d92348c からの差分で言う。

1. `claude/hooks/require_verify_before_stop.py` の 130 行目が、次の1行に置き換わっている(行頭の空白 12 字は変わらない)。
   - `# git は index の更新時刻と同じ秒に書き換えたファイルだけ中身を読み直すので、更新時刻も保持してコピーする`
2. `claude/hooks/require_verify_before_stop.py` のほかの行は変わっていない。
3. 1 のほかのファイルは、この記録のほかは d92348c と同じである。`docs/specs/` と `docs/adr/` は変わっていない。
4. `python -m unittest discover -s tests` が全部通る。

# 設計

コメントだけの変更で、動きは変わらないので、仕様(`docs/specs/require_verify_before_stop.py.md`)は直さない。書き換える行にも、その関数 `content_sig` にも ADR の番号は無い。仕様の「ADR」の節の 0011-1・0011-2 は、Stop フックが止める条件と確かめのコマンドの置き場の決定で、このコメントの言葉には効かないので、読む ADR は無く、ADR は書かない。

語は「保持」。Python の公式文書が `shutil.copy2` を「ファイルのメタデータを保持しようと」する(英語版 "attempts to preserve file metadata")と書いている。出典: https://docs.python.org/ja/3/library/shutil.html#shutil.copy2

## 手順

| 順 | する人 | 操作 |
|---|---|---|
| 1 | PG | `claude/hooks/require_verify_before_stop.py` の 130 行目の末尾「更新時刻も写す」を「更新時刻も保持してコピーする」に替える |
| 2 | PG | `python -m unittest discover -s tests` を走らせる |
| 3 | PG | `git diff d92348c --stat` で、変わったファイルがフックとこの記録だけかを見る |

## テスト一覧

コメントだけの変更なので、テストは作らない。

| 確かめ方 | 受け入れ条件 |
|---|---|
| `git diff d92348c -- claude/hooks/require_verify_before_stop.py` が、130 行目の1行の置き換えだけを示す | 1・2 |
| `git diff d92348c --stat` が、フックとこの記録の2ファイルだけを示す | 3 |
| `python -m unittest discover -s tests` が OK で終わる | 4 |

# 実装

- フックの 130 行目を、設計どおり「更新時刻も保持してコピーする」に替えた。
- `python -m unittest discover -s tests`: 64 件 OK(lint のコマンドは CLAUDE.md に無い)。
- `git diff d92348c -- claude/hooks`: 130 行目の1行の置き換えだけ。`--stat`: フックとこの記録の2ファイルだけ。

# レビュー

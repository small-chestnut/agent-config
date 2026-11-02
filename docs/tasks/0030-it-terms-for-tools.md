ステータス: 実装中

# ゴール

agent-config の文書(`claude/` 以下・README・リポジトリの CLAUDE.md・`.claude/rules/`・仕様・用語集と、hooks の docstring とコメント)で、IT の決まった用語が1つあるものを日常の言葉で言い換えている箇所が、その IT の用語になっている。全体の CLAUDE.md 原則3 の「言葉は、広く使われている呼び名で書いている。IT の用語があれば、その用語。」に、文書自身が沿う。

直す箇所は、日常の言葉が、IT の用語1つと同じものを指しているものだけ。

範囲外: ADR の本文(採用した ADR で書き換えるのは状態の行だけ)、用語集に行のある言葉とその定義の中の言葉(中身の印・確かめのコマンド・コマンドの頭・公開の入口・テストの大きさなど)、ふつうの日本語でも IT の現場で通じる言い回し(定石・業務の規則・ブランチ運用など)。

# 受け入れ条件

main(a5b2574)からの差分で言う。各行は、左の文が右の文に置き換わっている。

| 番号 | ファイル:行 | 前 | 後 |
|---|---|---|---|
| 1 | `claude/CLAUDE.md:109` | テストの道具のタグで | テストフレームワークのタグで |
| 2 | `claude/CLAUDE.md:110` | タグの無い道具では | タグの無いテストフレームワークでは |
| 3 | `claude/CLAUDE.md:44・47・48・49・50` | 横線 | 水平線 |
| 4 | `docs/用語集.md:36` | 返答の1本目の横線の下の文 | 返答の1本目の水平線の下の文 |
| 5 | `claude/CLAUDE.md:37` | ファイル名・行番号・コマンド名・エラー文は、広く使われている呼び名だけでは指す先が二通りに読めるときにだけ添えている。 | ファイル名・行番号・コマンド名・エラーメッセージは、広く使われている呼び名だけでは二通りに読めるときにだけ添えている。 |
| 6 | `claude/CLAUDE.md:130` | 置き場・名前の付け方 | 置き場・命名規則 |
| 7 | `CLAUDE.md:3` | テストは、この階層で | テストは、リポジトリのルートで |
| 8 | `claude/hooks/check_rule_documents_changed_by_shell.py:41・59・94` | リポジトリの根 / 根からのパス | リポジトリのルート / ルートからのパス |
| 9 | `claude/hooks/check_rule_length.py:4・70・85` | リポジトリの根 / 根からのパス | リポジトリのルート / ルートからのパス |
| 10 | `claude/hooks/check_rule_documents_changed_by_shell.py:5` | 決まりの文書の中身を一時ファイルに写す | 決まりの文書の中身のスナップショットを一時ファイルに取る |
| 11 | `claude/hooks/check_rule_documents_changed_by_shell.py:6・114・164` | 写し | スナップショット |
| 12 | `claude/hooks/block_history_erasing_push.py:5` | + か : で始まる指定(+main・:main) | + か : で始まる refspec(+main・:main) |
| 13 | `docs/specs/require_verify_before_stop.py.md:23` | 中身の印は、まだ追っていないファイルを足すと変わる。 | 中身の印は、未追跡のファイルを足すと変わる。 |
| 14 | `docs/specs/require_verify_before_stop.py.md:24` | 同じ大きさで書き換えても | 同じファイルサイズで書き換えても |
| 15 | `claude/skills/task-team-lead/SKILL.md:100` | コードの囲みで付けている | コードブロックで付けている |
| 16 | `claude/skills/task-team-lead/SKILL.md:101` | PL の会話を縮めるのは | PL の会話を圧縮するのは |
| 17 | `claude/skills/task-team-lead/SKILL.md:105・115` | 文脈 | コンテキスト |
| 18 | `claude/skills/task-team-lead/CLAUDE.md:48・56` | 文脈 | コンテキスト |
| 19 | `.claude/rules/global-claude-md.md:10` | 文脈やプロンプトインジェクション | コンテキストやプロンプトインジェクション |
| 20 | `claude/skills/ui-mockup/SKILL.md:12` | 色・文字の大きさ・部品の形は | 色・フォントサイズ・コンポーネントの形は |
| 21 | `claude/skills/task-team-pg/SKILL.md:59` | 確かめた画面の画像は | 確かめた画面のスクリーンショットは |
| 22 | `claude/skills/restructure-modules/SKILL.md:15` | ほかのブランチの変更とぶつからない | ほかのブランチの変更とコンフリクトしない |

23. 1〜22 のほかの行は、main と同じである。`docs/adr/` は変わっていない。
24. 1〜22 で変えた箇条書きの行は、どれも 60 字以内(`claude/hooks/check_rule_length.py` の数え方)。
25. `python -m unittest discover -s tests` が全部通る。

# 設計

文書と docstring・コメントだけの変更で、動きは変えない。`SKILL.md`・`CLAUDE.md` は決まりの文書そのものが仕様。`docs/specs/require_verify_before_stop.py.md` は言葉だけを直し、仕様の行の意味は変えない。

書き換える行に付いた ADR は、`claude/CLAUDE.md:107` の見出しの 0009-2 と、`task-team-pg/SKILL.md:59` の 0011-3。どちらも決定は変えず、言葉だけを直すので、ADR は書かない。両 ADR の本文の「道具」は、採用した ADR なので直さない。仕様の「ADR」の節は ADR の題の写しなので直さない。

用語集には足さない(IT の用語は、リポジトリで形か意味を決めたものだけを載せる)。

## 手順

| 番号 | する人 | すること |
|---|---|---|
| 1 | PG | 受け入れ条件 1〜22 の置き換えをする。前の文は各行の中で1か所だけなので、その字だけを置き換える(5 は行全体) |
| 2 | PG | 確かめ: 下の「テスト一覧」の確かめ方を全部走らせる |
| 3 | PG | コミットする。本文に理由を書く: 全体の CLAUDE.md 原則3 の「IT の用語があれば、その用語」に、agent-config の文書自身が沿っていなかった(PL が tool を「道具」と訳して利用者に伝わりにくかったのが発端) |
| 4 | PL | main にマージし、push し、agent-config の main のチェックアウトで `install.ps1 -Yes` を走らせる。`~/.claude/CLAUDE.md` の 109 行目に「テストフレームワーク」があるのを確かめる |

## テスト一覧

文書だけの変更なので、テストは作らない。確かめ方を並べる。

| 確かめ方 | 受け入れ条件 |
|---|---|
| `git diff a5b2574 --stat` が、受け入れ条件 1〜22 のファイルと `docs/tasks/0030-it-terms-for-tools.md` だけ | 23 |
| `git diff a5b2574 --word-diff` の各変更が、受け入れ条件の表の前と後の組だけ | 1〜23 |
| `git grep -n -E "道具\|横線\|リポジトリの根\|根からのパス\|写し\|写す\|コードの囲み\|文脈\|部品の形" -- claude CLAUDE.md .claude docs/specs docs/用語集.md` が何も返さない | 1〜4・8〜11・15・17〜20 |
| 変えた箇条書きの行を、`check_rule_length.rule_length` で数え、どれも 60 以下 | 24 |
| `python -m unittest discover -s tests` | 25 |

# 実装

# レビュー

ステータス: 設計レビュー中

# ゴール

AI が、終わったと言う前に、自分の変更を確かめている。画面が変わる変更は、AI が動かした画面のスクリーンショットを見て確かめ、報告にその画像を付ける。テストと lint は、Claude が自分で走らせて今の中身で通るまで、Stop フックがターンを終わらせない。確かめのコマンドの頭は、各リポジトリの `.claude/verify-commands.txt` に書く。

PL が調べたずれ: Anthropic の手引き(https://code.claude.com/docs/en/best-practices)は、AI が自分の仕事を確かめる手段(テスト・build・lint・ブラウザのスクリーンショット)を持つことを一番効くとし、確かめが通るまで Stop フックでターンを終わらせないことを勧めている。agent-config には、画面を見て確かめる決まりも Stop フックも無かった。

範囲外: 画面を見たかをフックで確かめること・Codex(`codex/AGENTS.md`)の側の確かめの仕組み・サブエージェントの終わり(SubagentStop)。

# 受け入れ条件

1. Stop フックは、ターンの始めから中身が変わり、今の中身で通っていない確かめのコマンドがあれば、その頭を並べてターンを止める。
2. Stop フックは、今の中身で一覧の確かめが全部通っていれば止めない。
3. Stop フックは、ターンの始めの印が無いか、ターンの始めから中身が変わっていなければ止めない。
4. 確かめのコマンドの頭で始まるコマンドが Bash か PowerShell で通ると、今の中身でその確かめが通ったと記録される。
5. パイプ・`;`・`&` を含むコマンドと、バックグラウンドで走らせたコマンドは、確かめとして数えない(`2>&1` は数える)。
6. 中身の印は、コミットしても、`docs/` の下だけを変えても変わらない。
7. 確かめのコマンドの一覧が無いリポジトリと、git の外では、フックは何もしない。
8. `claude/user-settings.json` の UserPromptSubmit・PostToolUse(Bash|PowerShell)・Stop から、フックが呼ばれる。
9. agent-config に `.claude/verify-commands.txt` があり、中身は `python -m unittest` の1行。
10. グローバルの CLAUDE.md の原則3 に、確かめのコマンドの頭を一覧に書く行と、画面が変わる変更をスクリーンショットで確かめて報告に付ける行がある。
11. `task-team-pg` に、確かめた画面の画像を記録のフォルダに置き、実装の節から指す行がある。
12. README に、Stop フックの意図と、画面の確かめの意図がある。
13. `docs/用語集.md` に、確かめのコマンド・確かめのコマンドの一覧・中身の印・ターンの始めの印・確かめの記録の行がある。
14. どの SKILL.md の箇条書きの行も 60 字以内(`python -m unittest discover -s tests` が通る)。

# 設計

決定は [ADR 0011-1](../adr/0011-1-stop-hook-checks-evidence.md)・[ADR 0011-2](../adr/0011-2-verify-commands-file.md)・[ADR 0011-3](../adr/0011-3-screenshot-check.md)(どれも採用)。用語は [docs/用語集.md](../用語集.md)(この設計と同じコミットで SE が足した)。書き換える行に付いた ADR の参照は無い。する人は、どの手順も PG。

出典: Stop フックの入力・止め方・8回続けて止めると終わる上限は https://code.claude.com/docs/en/hooks の Stop の節。Bash と PowerShell のコマンドが 0 以外で終わると PostToolUse ではなく PostToolUseFailure になることは、同じページの PostToolUseFailure の節。UserPromptSubmit が、利用者の入力のほか、ほかのセッションからの知らせでも走ることは、同じページの UserPromptSubmit の節。

## 置くファイル

| ファイル | 中身 |
|---|---|
| `claude/hooks/require_verify_before_stop.py` | フック。引数 `turn-start`・`record`・`stop` で動きを分ける |
| `tests/test_require_verify_before_stop.py` | フックのテスト(下のテスト一覧) |
| `.claude/verify-commands.txt` | agent-config の確かめのコマンドの一覧。中身は `python -m unittest` の1行 |

## データ

- 確かめのコマンドの一覧: `<リポジトリの根>/.claude/verify-commands.txt`。1行に1つの頭。空の行と `#` で始まる行は読まない。リポジトリの根は `git -C <フックの cwd> rev-parse --show-toplevel`。
- 中身の印: 作業ツリーの中身から作る git の tree の id。作り方:
  1. `git rev-parse --git-path index` の index を一時ファイルに写す(無ければ空のまま)。
  2. 環境変数 `GIT_INDEX_FILE` にその一時ファイルを指して、`git add -A`・`git rm -r --cached -q --ignore-unmatch -- docs`・`git write-tree` を、リポジトリの根で順に走らせる。最後の出力が中身の印。
  3. 一時ファイルを消す。
  - 本物の index は変わらない。git の objects には、まだコミットしていない中身の blob が足される(git gc が後で消す)。
- 確かめの記録: `<git rev-parse --git-common-dir>/claude-verify.json`。worktree どうしで1つを分け合う。形:

```json
{"turn_start": {"<session_id>": "<中身の印>"}, "passed": {"<中身の印>": ["<頭>"]}}
```

  - `turn_start` と `passed` は、それぞれ新しい50件だけを残し、古い方から捨てる。
  - 書くときは一時ファイルに書いて `os.replace` で置き換える。読めないか壊れていたら、空として扱う。

## フックの動き

どの引数でも、git の外か、確かめのコマンドの一覧が無いか、頭が1つも無ければ、何もせず exit 0。途中で例外が出ても exit 0。

| 引数 | 呼ぶ所 | 動き |
|---|---|---|
| `turn-start` | UserPromptSubmit | `turn_start[session_id]` に今の中身の印を書く。exit 0 |
| `record` | PostToolUse(Bash\|PowerShell) | 数える頭(下)があれば、`passed[今の中身の印]` にその頭を足す。exit 0 |
| `stop` | Stop | 下の「止めるとき」なら、通っていない頭を stderr に並べて exit 2。それ以外は exit 0 |

数える頭: `tool_input.command` の前後の空白を除いた文が、頭と同じか、「頭 + 空白」で始まる頭。ただし次のどれかなら1つも数えない。
- `tool_input.run_in_background` が true。
- 文から `2>&1` を除いたあとに、`|`・`;`・`&`・改行のどれかがある。

止めるとき: `turn_start[session_id]` があり、それが今の中身の印と違い、一覧の頭のうち `passed[今の中身の印]` に無いものが1つ以上あるとき。`stop_hook_active` は見ない(8回続けて止めると Claude Code が終わらせる)。

stderr に出す文(`<頭>` は通っていない頭ごとに1行):

```
このターンで中身が変わりましたが、今の中身で通っていない確かめのコマンドがあります。
リポジトリの中で走らせて通してから終えてください(パイプ・;・&・バックグラウンドを付けると数えません):
  <頭>
```

ADR の参照: モジュールの docstring の1行目の末尾に `(ADR 0011-1)`、一覧のパスの定数の行のコメントに `# (ADR 0011-2)`。

## 手順: フックを登録する

`claude/user-settings.json` の `hooks` を、次のとおりにする。コマンドの形は、既にあるフックと同じ `P=python3; python3 -c '' 2>/dev/null || P=python; "$P" "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/require_verify_before_stop.py" <引数>`。

- `UserPromptSubmit` を足す: matcher なしで、引数 `turn-start` の1つ。
- `PostToolUse` の matcher `Bash|PowerShell` の hooks の最後に、引数 `record` を足す。
- `Stop` を足す: matcher なしで、引数 `stop` の1つ。

`~/.claude` への配置は、マージの後に PL が `install.ps1 -Yes` でする(CLAUDE.md 原則1)。

## 手順: 規則の文書を直す

下の行を、そのとおりの文で入れる。字数は `rule_length` で数え済み(どれも 60 字以内)。

### `claude/CLAUDE.md`(原則3「目指す状態: 変更が意図どおりかを自分で確かめてから、終わったと報告している」の下)

- 「テストと lint のコマンドが無いリポジトリには、最初の作業で足している。」の後に足す:

```
- テストと lint のコマンドの頭は、`.claude/verify-commands.txt` にも1行ずつ書いている。(ADR 0011-2)
```

- 「終わったという報告には、テストと lint を走らせた結果がある。」の後に足す:

```
- 画面が変わる変更は、動かした画面のスクリーンショットを撮って見て確かめている。(ADR 0011-3)
- その報告には、確かめた画面のスクリーンショットがある。(ADR 0011-3)
```

### `claude/skills/task-team-pg/SKILL.md`(「目指す状態: ターンが終わるとき、次の子セッションが動ける」の下)

- 「コミットし、流したテストと lint とその結果を「実装」の節に書いている。」の後に足す:

```
- 確かめた画面の画像は記録のフォルダに置き、実装の節から指している。(ADR 0011-3)
```

### `README.md`

- 「プロンプト層(CLAUDE.md / AGENTS.md)の意図」の「- **シェルから書いた決まりの文書にも、同じ2つを掛ける**。」の項目の後に、次の項目を足す。

```
- **終わる前の確かめは、Stop フックが守らせる**(ADR 0011-1・0011-2)。CLAUDE.md に「確かめてから終える」と書くだけでは、
  モデルの判断で確かめずに終えることがあるため(公式の手引き https://code.claude.com/docs/en/best-practices も、
  例外の無い決まりはフックに置くよう勧める)、`hooks/require_verify_before_stop.py` が、ターンの始め(UserPromptSubmit)に
  中身の印を取り、Bash か PowerShell で確かめのコマンド(各リポジトリの `.claude/verify-commands.txt` に1行ずつ書いた頭)が
  通るたびに、そのときの中身の印に通ったと記録し、ターンの終わり(Stop)に、中身が変わったのに今の中身で通っていない
  確かめがあれば、並べて止める。フックはコマンドを自分では走らせない。フックが走らせるコマンドは permissions と
  サンドボックスを通らず、リポジトリに書かれたコマンドを確かめずに走らせる口になるため。頭で数えるのは、書いている間に
  変えた所の小さいテストだけを流しても通るようにするため。中身の印は `docs/` を除いた git の tree なので、コミットしても、
  記録や ADR だけを変えても変わらない。一覧の無いリポジトリでは何もしない。ツールを使わずに8回続けて止めると、
  Claude Code がターンを終わらせる
```

- 「セッションの役割分割」の「- **テストを流す時と量は、…**。」の下の「  - 書いている間(手元・PG): 変えた所の小さいテストだけ(数秒〜1分)」の後に、次の行を足す。

```
  - 画面が変わる変更(手元・PG): 動かした画面のスクリーンショットを見て、記録のフォルダに画像を置く(ADR 0011-3)。
    大きいテストは決めた操作の結果しか見ないので、崩れた配置や読めない字はこちらで見る
```

## コミット

1コミット。件名: `ターンの終わりに、今の中身で確かめが通っているかを Stop フックで見る`。

- 本文に、ADR 0011-1・0011-2・0011-3 を実装したことと、公式の手引きが、AI が自分の仕事を確かめる手段を持つことを一番効くとし、確かめが通るまで Stop フックでターンを終わらせることを勧めていること(https://code.claude.com/docs/en/best-practices)を書く。
- この記録の「実装」の節も同じコミットに入れる。

## テスト一覧

| テスト名 | 大きさ | 受け入れ条件 |
|---|---|---|
| `test_確かめのコマンドの一覧は空の行と#の行を読まない` | 小 | 4 |
| `test_頭と同じか頭と空白で始まるコマンドを確かめとして数える` | 小 | 4 |
| `test_頭の直後が空白でなければ数えない` | 小 | 4 |
| `test_パイプとセミコロンとアンドと改行を含むコマンドは数えない` | 小 | 5 |
| `test_2>&1を付けたコマンドは数える` | 小 | 5 |
| `test_バックグラウンドで走らせたコマンドは数えない` | 小 | 5 |
| `test_ターンの始めの印が無ければ止めない` | 小 | 3 |
| `test_ターンの始めから中身が変わっていなければ止めない` | 小 | 3 |
| `test_今の中身で通っていない確かめの頭を返す` | 小 | 1 |
| `test_今の中身で全部の確かめが通っていれば止めない` | 小 | 2 |
| `test_コミットしても中身の印は変わらない` | 中 | 6 |
| `test_docsの下だけを変えても中身の印は変わらない` | 中 | 6 |
| `test_まだ追っていないファイルを足すと中身の印が変わる` | 中 | 1 |
| `test_確かめを通すまでStopフックが止め通したら止めない` | 中 | 1・2・4 |
| `test_一覧の無いリポジトリではフックが何もしない` | 中 | 7 |
| `test_gitの外ではフックが何もしない` | 中 | 7 |
| `claude/user-settings.json` を読み、上の3か所から上の引数で呼ばれている | — | 8 |
| `.claude/verify-commands.txt` の中身が `python -m unittest` の1行 | — | 9 |
| `git diff main -- claude/CLAUDE.md claude/skills README.md` を読み、上の文が上の位置にそのまま入っている | — | 10・11・12 |
| `docs/用語集.md` に、確かめのコマンド・確かめのコマンドの一覧・中身の印・ターンの始めの印・確かめの記録の行がある | — | 13 |
| `test_どのSKILL_mdの箇条書きの行も60字以内`(既にある) | 小 | 14 |

- 小のテストは、中身の印と確かめの記録を引数で渡す関数を呼ぶ(git もファイルも使わない)。関数の名前と形は PG が決める。
- 中のテストは、既にあるフックのテストと同じく、一時的な git リポジトリを作り、フックを `subprocess` で走らせる。外とのつなぎ目は git と確かめの記録のファイル。
- `test_確かめを通すまでStopフックが止め通したら止めない` の流れ: `turn-start` → ファイルを変える → `stop` が exit 2 で stderr に頭がある → 頭で始まるコマンドの PostToolUse の入力で `record` → `stop` が exit 0 → もう一度ファイルを変える → `stop` が exit 2(前の中身で通った確かめは数えない)。

lint のコマンドはこのリポジトリに無い。

# 実装

# レビュー

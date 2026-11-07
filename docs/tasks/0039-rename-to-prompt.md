ステータス: 実装レビュー済み

# 進み具合

- 利用者待ち: なし
- [x] 1. やり方を決める(済んだ印: 受け入れ条件 6 件・テスト一覧 6 件)
- [x] 2. フックの知らせを「このコマンドでプロンプトに足した行です」にする(前: 1)(済んだ印: テスト一覧の 1 が OK(失敗→成功を確認))
- [x] 3. フック・テスト・skill・hooks の決まりの中の呼び名を「プロンプト」にする(前: 1)(済んだ印: テスト一覧の 2〜6 が OK)
- [x] 4. できたものを見直す(前: 2・3)(済んだ印: 実装レビューの指摘 0 件)

# ゴール

「決まりの文書」という呼び名が、フックの知らせと、このリポジトリの文書・コード・テストから消え、「プロンプト」になる。

なぜ: 利用者が「決まりの文書」という言葉を嫌った。全体の CLAUDE.md の決まりでは、言葉は広く使われている呼び名で書き、IT の用語があればその用語を使う。「プロンプト」は AI に渡す指示の文を指す IT の用語で、skill `prompt-structure` も CLAUDE.md や skill を「AI への指示(プロンプト)」と呼んでいる。

範囲外: ファイル名とコードの名前(`rule_documents`・`RULE_DOCUMENT_NAMES`・`is_rule_document`・`.claude/rule-documents.txt` など)、ADR の本文、「決まりを書く文書」「決まりの行」「決まりの1行」など別の言い方、用語集、main へのマージ・push・`install.ps1 -Yes`(PL がする)。

# 受け入れ条件

1. シェルのフック(`check_rule_documents_changed_by_shell.py`)が足した行を問うとき、知らせは「このコマンドでプロンプトに足した行です。」で始まる。
2. 次の 9 ファイルは、main の中身の「決まりの文書」を「プロンプト」に替えたものと同じで、ほかは変わっていない。ただし `tests/test_check_rule_documents_changed_by_shell.py` には、テスト一覧の 1 のテストが足してある。
   - `claude/hooks/check_rule_length.py`
   - `claude/hooks/ask_removable_words.py`
   - `claude/hooks/check_rule_documents_changed_by_shell.py`
   - `tests/test_check_rule_length.py`
   - `tests/test_ask_removable_words.py`
   - `tests/test_check_rule_documents_changed_by_shell.py`
   - `.claude/rules/hooks.md`
   - `claude/skills/task-team-se/SKILL.md`
   - `docs/specs/check_rule_documents_changed_by_shell.py.md`
3. 仕様 `claude/skills/task-team-se/SKILL.md`(プロンプトなので、それ自体が仕様)の目指す状態「機能の今の動きは、モジュールの仕様1つにある」の下の2行が、次の2行になっている。
   ```
   - SKILL.md などプロンプトがモジュールの中身なら、その文書が仕様。
   - プロンプトが仕様なら、番号は行と見出しにだけ付ける。(ADR 0010-2)
   ```
4. 仕様 `docs/specs/check_rule_documents_changed_by_shell.py.md` の「足した行」の節の2行が、次の2行になっている。
   ```
   - プロンプトは、`check_rule_length.py` と同じ決め方で、git が無視するファイルを除く。
   - コマンドで作ったプロンプトは、全部の行を足した行とする。
   ```
5. `docs/adr/` と `docs/tasks/` を除くリポジトリの中に、「決まりの文書」が1つも無い。`docs/adr/` と `docs/用語集.md` は変わっていない。
6. リポジトリのルートで `python -m unittest discover -s tests` が全部 OK。

# 設計

## 書き換える所と ADR

- 書き換えるのは、受け入れ条件 2 の 9 ファイルにある「決まりの文書」26 か所(main の d1bbf4b で数えた。フック 12・テスト 9・skill 2・仕様 2・hooks の決まり 1)。どれも、その字を「プロンプト」に替えるだけで文が通る(9 ファイルとも、替えた後の文を読んで確かめた)。
- テストの名前とクラスの名前(`class 決まりの文書` など)も、同じく字を替える。Python は名前にカタカナを使える。
- 付いている ADR の番号は、`task-team-se/SKILL.md` の2行目の 0010-2 だけ。0010-2 は仕様に ADR の番号を並べる決定で、呼び名には触れない。行末の「(ADR 0010-2)」は残す。
- 仕様 `docs/specs/check_rule_documents_changed_by_shell.py.md` は、この設計のコミットで直した(受け入れ条件 4)。「ADR」の節は「なし」のまま。
- 「決まりの文書」が出てくる ADR 0010-1・0027-1 は、どちらも状態「採用」。採用した ADR で書き換えるのは状態の行だけ(skill `task-team-se`)なので、本文は替えない。
- ファイル名とコードの名前は、英語の名前で、利用者が嫌った日本語の呼び名ではない。名前を替えると、`install.ps1` と設定のフックの登録にも及ぶので、このタスクでは替えない。
- 「プロンプト」は IT の用語なので、用語集には足さない。

## 手順(する人: どれも PG)

1. テスト一覧の 1 のテストを `tests/test_check_rule_documents_changed_by_shell.py` のクラス `コマンドの前後の動き` に足し、失敗することを確かめる。中身は、`test_コマンドで長い決まりを足すと知らせと問いが返る` と同じく長い行を2行書いて `after` を走らせ、stderr に「このコマンドでプロンプトに足した行です。」があることを確かめる。
2. 受け入れ条件 2 の 9 ファイルのうち仕様を除く 8 ファイルで、「決まりの文書」をすべて「プロンプト」に替える(仕様は設計のコミットで替えてある)。ほかの字は変えない。
3. テスト一覧の確かめ方を順に行う。
4. 1〜2 を1つのコミットにする。本文に、利用者がこの呼び名を嫌ったことと、IT の用語に揃えたことを書く。

## テスト一覧

テストを作るのは、画面に出る知らせ(受け入れ条件 1)だけ。ほかは呼び名を替えるだけなので、確かめ方を並べる。

| # | テスト名(確かめ方) | 大きさ | 受け入れ条件 |
|---|---|---|---|
| 1 | `test_コマンドで足した行はプロンプトに足した行と知らせる` | 中(一時フォルダに git のリポジトリを作り、フックを別のプロセスで走らせる。この test ファイルのほかの中のテストと同じく、タグは付けない) | 1 |
| 2 | 受け入れ条件 2 の 9 ファイルについて、`git show main:<ファイル>` の「決まりの文書」を「プロンプト」に替えたものと `git show HEAD:<ファイル>` を比べる。`tests/test_check_rule_documents_changed_by_shell.py` は差が 1 のテストの行を足しただけ、ほかの 8 ファイルは差が無い(作業ツリーの改行の違いを避けるため、コミットしてから比べる) | — | 2 |
| 3 | `git show HEAD:claude/skills/task-team-se/SKILL.md` に受け入れ条件 3 の2行がある | — | 3 |
| 4 | `git show HEAD:docs/specs/check_rule_documents_changed_by_shell.py.md` に受け入れ条件 4 の2行がある | — | 4 |
| 5 | `git grep -n "決まりの文書" -- . ":!docs/adr" ":!docs/tasks"` が 0 件で、`git diff main -- docs/adr docs/用語集.md` が空 | — | 5 |
| 6 | `python -m unittest discover -s tests` が全部 OK | 小・中 | 6 |

# 実装

コミット: 受け入れ条件 2 の 8 ファイル(仕様を除く)を1コミット(「0039: 「決まりの文書」を「プロンプト」と呼ぶ」)。

- 1: テスト `test_コマンドで足した行はプロンプトに足した行と知らせる` を先に足し、旧い文言で失敗することを確かめてから直した。OK。
- 2: 9 ファイルを `git show main:` の「決まりの文書」→「プロンプト」と `HEAD:` で比べた。差は、test ファイルの足した6行だけで、ほかの8ファイルは 0。
- 3・4: `git show HEAD:` に、受け入れ条件 3 の2行と 4 の2行がある。
- 5: `git grep -n "決まりの文書" -- . ":!docs/adr" ":!docs/tasks"` が 0 件。`git diff main -- docs/adr docs/用語集.md` が空。
- 6: `python -m unittest discover -s tests` が 75 件 OK。lint のコマンドは CLAUDE.md に無い。
- 注: コミット前の Bash で、フックが「プロンプトに足した行」3 行(hooks.md:18、task-team-se/SKILL.md:116・117)の消せる語を問うた。設計が字の置き換えだけと決めているので、語は消していない。

# レビュー

実装: 指摘なし

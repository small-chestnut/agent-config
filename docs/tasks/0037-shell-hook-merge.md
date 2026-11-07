ステータス: 実装中

# 進み具合

- 利用者待ち: なし
- [x] 1. やり方を決める(済んだ印: 受け入れ条件 7 件・テスト一覧 7 件・ADR の案 0 件)
- [ ] 2. 取り込むコマンドで入った行を問わない(前: 1)(済んだ印: テスト一覧の 1・3・5・7 が OK)
- [ ] 3. 取り込むコマンドの中でも、Claude が書いた行は問う(前: 2)(済んだ印: テスト一覧の 2・4・6 が OK)
- [ ] 4. ルールに「なぜ」を書き、テストを全部流す(前: 3)(済んだ印: 受け入れ条件 6・7 を満たす)
- [ ] 5. できたものを見直す(前: 4)(済んだ印: レビューの節に結果がある)

# ゴール

シェルで `git merge --ff-only origin/main` などを走らせたとき、PostToolUse フック `check_rule_documents_changed_by_shell.py` が、git がほかのコミットから持ってきた決まりの文書の行に、字数の知らせも「消しても意味が変わらない語を探して」の問いも返さない。Claude がシェルで書いた行には、今までどおり返す。

なぜ: 取り込んだ行は、既にレビューとマージを経た、利用者やほかの人の決定。問いに従うと Claude がそれを勝手に書き換え、要らない差分を作る。複数の PC やほかの人とリポジトリを共有していると、取り込むたびに起きる。

範囲外: `git stash pop`・`git restore --source=<コミット>` のように、HEAD にもインデックスにも無い中身を作業ツリーにだけ戻す行(今のまま問う)。`check_rule_length.py`・`ask_removable_words.py`(Edit・Write のフック)。`claude/user-settings.json` のフックの登録。main へのマージ・push・`install.ps1 -Yes`(PL がする)。

# 受け入れ条件

1〜5 は、仕様 `docs/specs/check_rule_documents_changed_by_shell.py.md` の「取り込んだ行」の節の文。

1. フックは、git の merge・pull・checkout・switch・rebase・cherry-pick・reset・restore・revert・am を走らせたコマンドを、取り込むコマンドとする。
2. 取り込むコマンドでは、コマンドの後の HEAD かインデックスの中身と同じ行を、足した行に数えない。
3. 取り込むコマンドでは、git が書いた衝突の印の行も、足した行に数えない。
4. 取り込むコマンドでも、HEAD ともインデックスとも違う行は、足した行に数える。
5. 取り込まないコマンドでは、コミットした行も足した行に数える。
6. `.claude/rules/hooks.md` の、目指す状態「Bash や PowerShell で書いた決まりの文書も、素通りしていない」とその下の2行の次に、次の目指す状態と2行がある。ほかの行は変わっていない。
   ```
   ### 目指す状態: 取り込んだだけの決まりの行を、Claude に書き換えさせない

   - 取り込むコマンドで git が持ってきた行には、字数の数えも問いも掛けていない。
   - 取り込んだ行は、既にレビューを経た決定で、直すと要らない差分ができる。
   ```
7. リポジトリのルートで `python -m unittest discover -s tests` が全部 OK(今あるテストを含む)。

# 設計

## 書き換える所と ADR

- `claude/hooks/check_rule_documents_changed_by_shell.py`。このファイル・テスト・`.claude/rules/hooks.md` を「ADR」で探して 0 件。仕様は無かったので、この設計のコミットで作った(`## ADR` は「なし」)。読む ADR は無い。
- ADR は書かない。フックの見る行を、ルールの「シェルで書いた行」の意図に合わせる直しで、構造・依存・インターフェースの決定ではない。
- 仕様と用語集(「取り込むコマンド」の行)は、この設計のコミットで書いた。PG は直さない。

## 置くもの(どれも `claude/hooks/check_rule_documents_changed_by_shell.py`)

- `IMPORTING_COMMAND`: `git` の後に、`-C <パス>`・`-c <値>`・`--<名前>[=<値>]` の形のオプションを0個以上はさみ、受け入れ条件 1 の10個のサブコマンドのどれかが続き、その後が空白・行の終わり・`;`・`&`・`|`・`)` のどれかであるのに当たる正規表現(`git merge-base` には当たらない)。
- `brings_other_commits(command: str) -> bool`: command に `IMPORTING_COMMAND` が当たるか。
- `CONFLICT_MARKER`: `<<<<<<<`・`=======`・`>>>>>>>`・`|||||||` のどれかで始まり、その後が空白か行の終わりの行に当たる正規表現。
- `git_versions(root: Path, rel: str) -> list[str]`: `git show HEAD:<rel>` と、`git show :<n>:<rel>`(n は 0〜3)のうち、成功したものの中身。`check_rule_length.git` を使う。
- `imported_lines(text: str, versions: list[str]) -> set[int]`: text の行番号のうち、versions のどれか1つで `added_lines(<その版>, text)` に入らない行と、`CONFLICT_MARKER` に当たる行。
- `findings(before, roots, command: str)`: 引数に command を足す。`brings_other_commits(command)` なら、ファイルごとに `new_lines` から `imported_lines(text, git_versions(root, rel))` を引いてから、`too_long` と `asked_lines` に渡す。
- `after_command`: `findings` に、event の `tool_input.command`(無ければ空の文字列)を渡す。
- モジュールの docstring に、「取り込むコマンドでは、HEAD かインデックスと同じ行と衝突の印の行を問わない」旨の1行を足す。

## 手順(する人: どれも PG)

1. テスト一覧の 3・7 を先に書き、今のコードで失敗するのを見る(バグの再現)。
2. 置くものを書き、テスト一覧の 1・3・5・7 を通す。
3. テスト一覧の 2・4・6 を書いて通す。
4. `.claude/rules/hooks.md` に受け入れ条件 6 の目指す状態と2行を足す。目指す状態の前後には空の行を1つずつ。
5. `python -m unittest discover -s tests` を流す。
6. コミットの本文に、ゴールの「なぜ」を書く。

## テスト一覧

テストは `tests/test_check_rule_documents_changed_by_shell.py` に足す。1・2 はクラス「取り込むコマンド」、3〜7 は今あるクラス「コマンドの前後の動き」(setUp の一時的な git リポジトリを使い、event の command を各テストで書き換える)。中のテストに印を付けないのは、このファイルの今あるテスト(git を走らせる中)に印が無いのに揃えるため。

3〜7 では、before と after の間で、event の command と同じ git のコマンドを、テストが一時的なリポジトリで走らせる。別のブランチは `git checkout -q -b other` で作り、`git checkout -q -` で戻る。

| # | テスト名 | 大きさ | 受け入れ条件 | やること |
|---|---|---|---|---|
| 1 | `test_取り込むgitのコマンドを見分ける` | 小 | 1 | `git merge --ff-only origin/main`・`git -C x pull`・`cd a && git checkout main`・`git cherry-pick abc` が True |
| 2 | `test_取り込まないコマンドは見分けない` | 小 | 1・5 | `git commit -am x`・`git add .`・`git stash pop`・`git log --grep merge`・`git merge-base a b`・`python edit.py` が False |
| 3 | `test_早送りで取り込んだ行は問わない` | 中 | 2 | other に長い行を足してコミット → 戻る → before → `git merge --ff-only other` → after が exit 0 |
| 4 | `test_取り込むコマンドの後に書いた行は問う` | 中 | 4 | 3 と同じ早送りの後、HEAD に無い長い行を3行目に書く(command は `git merge --ff-only other && python edit.py`) → after が exit 2 で、`CLAUDE.md:3` があり `CLAUDE.md:2` が無い |
| 5 | `test_衝突した取り込みでは衝突の印と両方の行を問わない` | 中 | 3 | other と元のブランチで1行目を別の長い行に書き換えて各々コミット → before → `git merge other`(衝突で失敗する) → after が exit 0 |
| 6 | `test_取り込まないコマンドでコミットした行は問う` | 中 | 5 | before → 長い行を2行目に足して `git commit -qam x`(command は `python edit.py && git commit -qam x`) → after が exit 2 で `CLAUDE.md:2` がある |
| 7 | `test_変更を捨ててHEADに戻した行は問わない` | 中 | 2 | 1行目を `- 前の変更` に書き換えておく → before → `git restore CLAUDE.md` → after が exit 0 |
| ― | `python -m unittest discover -s tests` が全部 OK | ― | 7 | |
| ― | `git diff` で `.claude/rules/hooks.md` が、足した目指す状態と2行(と空の行)だけ | ― | 6 | |

## 作業の前提

# 実装

# レビュー

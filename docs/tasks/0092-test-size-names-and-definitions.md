# 0092-test-size-names-and-definitions

ステータス: 設計レビュー中
PC: Reo-Desktop

## 進捗

- 利用者待ち: なし
- [x] 1. やり方を決める(完了条件: 利用者が要件 R1・R2 を進めると言っている)
- [/] 2. 書き換える文が、要件とほかの決まりに合うかを確かめる(依存: 1)(完了条件: 設計レビューに、直さないと通せない指摘が残っていない)
- [ ] 3. 規則とテストの呼び名と、分け方の置き場所を書き換える(依存: 2)(完了条件: R1 と R2 の受け入れ条件を確かめた結果が「実装」の節にある)
- [ ] 4. 書き換えた文書を確かめる(依存: 3)(完了条件: 実装レビューに、直さないと通せない指摘が残っていない)

## 難しさ

- SE: 高(どの文書のどの行を直し、定義をどこに置くかを、規則・ADR・出典から決める)
- PG: 低(書き換える文は設計で決まり、手順のとおりに実行する)
- QA: 高(分け方の置き方と文が、要件とほかの決まりに合うかを、自分で見分ける)

## ゴール

規則が、テストサイズを small・medium・large と呼び、サイズに触れるときには、その分け方がもう読まれている。

範囲外: テスト一覧の「大は、利用者の主な使い方1本につき1つまで」の中身(置くかどうかが回ごとに割れる件)と、ほかのリポジトリ(LogiFee・atcoder・live-subtitles・NekoShift)の文書の呼び名と、採用済みの ADR の文。

## 要件

### R1 呼び名を small・medium・large にする

- 要件: 規則とテストが、テストサイズを、小・中・大でなく、small・medium・large と呼ぶ。
- なぜ: 小・中・大という呼び名が気持ち悪い。small・medium・large のテストサイズと言いたい。
- 受け入れ条件 R1-1: `claude/`・このリポジトリの CLAUDE.md・`tests/` に、テストサイズを指す「小」「中」「大」が1つも無い。

### R2 サイズに触れる所では、分け方が読める

- 要件: テストサイズに触れる規則を読むときには、サイズの分け方も読まれている。分け方は、明確な出典を指せるなら、規則に書き直さない。
- なぜ: 基準を知らないまま、だいたいの見当でサイズを決められては困る。見るべき時に見るべき規則を参照できていないのは、読む量を減らすことより前の問題。明確な出典があるものは、用語集に知られている IT の用語を載せないのと同じで、書き直さなくてよい。
- 受け入れ条件 R2-1: テストのファイルを開いていない新しいセッションに、localhost の DB につなげるテスト・localhost で画面を操作するテスト・1つのプロセスで速さを測るテストのサイズを聞くと、medium・large・large と答える。
- 受け入れ条件 R2-2: サイズの分け方は、1つの文書にだけある。

### 分けたタスク

なし

### 決まっていない問い

なし

## 設計

### ADR

- [0092-1](../adr/0092-1-point-to-google-test-sizes.md)(提案。0009-1 を置き換える)・[0009-1](../adr/0009-1-test-size-by-resources.md)(置き換え済み(0092-1))

### 置くファイルと名前・データ

文は、下のとおりに書く。「→」の右の文を、ほかの語に替えない。

1. `claude/CLAUDE.md`(R1・R2)
   - 「### 目指す状態: テストは、テストサイズごとに決まった時に実行されている(ADR 0009-3)」の前に、次を足す。

```markdown
### 目指す状態: テストサイズは、テストが使う資源で決まっている(ADR 0092-1)

- テストサイズは、本『Software Engineering at Google』の small・medium・large で分ける。ただし、ブラウザかアプリの画面を操作するテストと、速さを測るテストは、large にする。

```

   - 「- 書いている間は、変えた所の小のテストだけを実行する。」→「- 書いている間は、変えた所の small のテストだけを実行する。」
   - 「- CI があれば、マージの前に小と中を、後に大を CI が実行し、成功を待つ。」→「- CI があれば、マージの前に small と medium を、後に large を CI が実行し、成功を待つ。」
   - 「- CI が無ければ、マージの前に、小と中の全部と、変えた使い方を確かめる大を実行する。」→「- CI が無ければ、マージの前に、small と medium の全部と、変えた使い方を確かめる large を実行する。」
2. `claude/rules/test-size.md`(R1・R2-2)
   - 「### 目指す状態: テストサイズは、テストが使う資源で決まっている(ADR 0009-1)」の見出しと、その下の3行と、前後の空行の1つを消す。見出しは1のとおり `claude/CLAUDE.md` に移す。
   - 「- 中と大には、テストフレームワークのタグで `medium`・`large` を付ける。」→「- medium と large のテストには、テストフレームワークのタグで `medium`・`large` を付ける。」
   - 「- タグの無いテストフレームワークでは、中と大のテストのファイル名の頭に `medium_`・`large_` を付ける。(ADR 0073-1)」→「- タグの無いテストフレームワークでは、medium と large のテストのファイル名の頭に `medium_`・`large_` を付ける。(ADR 0073-1)」
3. `claude/rules/claude-md.md`(R1): 「- リポジトリ直下の CLAUDE.md に、小だけ・小と中・大を実行するコマンドを置く。」→「- リポジトリ直下の CLAUDE.md に、small のテストだけ・small と medium のテスト・large のテストだけを実行するコマンドを、それぞれ置く。」
4. `claude/skills/task-team-pg/SKILL.md`(R1): 「- CI が無ければ、QA に頼む前に、小と中の全部と、変えた使い方を確かめる大を実行する。(ADR 0009-3)」→「- CI が無ければ、QA に頼む前に、small と medium の全部と、変えた使い方を確かめる large を実行する。(ADR 0009-3)」
5. `claude/skills/task-team-test-list/SKILL.md`(R1)
   - 「- テストサイズが小と中のテストは、」→「- テストサイズが small と medium のテストは、」(行の残りは変えない)
   - 「- 大は、利用者の主な使い方1本につき1つまで。(ADR 0005-1)」→「- large のテストは、利用者の主な使い方1本につき1つまで。(ADR 0005-1)」
6. このリポジトリの `CLAUDE.md`(R1)
   - 「- 中のテストは、ファイル名の頭に `medium_` を付ける。`medium_` の付いていないテストは小。(ADR 0072-1)」→「- medium のテストは、ファイル名の頭に `medium_` を付ける。`medium_` の付いていないテストは small。(ADR 0072-1)」
   - 「- 小だけは、」→「- small だけは、」(行の残りは変えない)
   - 「- 小と中は、`python -m unittest discover -s tests -p "*test_*.py"`。大のテストは無い。(ADR 0072-1)」→「- small と medium は、`python -m unittest discover -s tests -p "*test_*.py"`。large のテストは無い。(ADR 0072-1)」
7. `tests/` の docstring(R1)
   - `medium_test_add_team_skill_to_team_roles.py`・`medium_test_ask_about_written_lines.py`・`medium_test_check_rule_documents_changed_by_shell.py`・`medium_test_global_claude_md_length.py`・`medium_test_require_verify_before_stop.py`・`medium_test_rule_document_added_lines.py`・`medium_test_team_kanban_fields.py`: 「使うので中。」→「使うので medium。」
   - `test_block_history_erasing_push.py`: 「ので、小。」→「ので、small。」
   - `test_push_after_ticket_commit.py`・`test_remind_pin_after_starting_se.py`: 「終わる小。」→「終わる small。」

### 手順

1. 上のファイルを書き換え、ここに書かれていない行と ADR の番号はそのまま残す。(R1・R2)
2. small と medium のテストを全部実行する(全体の CLAUDE.md の字数のテストを含む。SE が数えた書き換え後の字数は 4,274 字)。(R1・R2)
3. テスト一覧の確かめ方を実行し、結果を「実装」の節に書く。(R1・R2)

### テスト一覧

コードは変えないので、作るテストも消すテストも無い。

| テスト名 | テストサイズ | 受け入れ条件 |
|---|---|---|
| 確かめ方: `claude/`・`CLAUDE.md`・`tests/` を `[小中大]` で検索し、テストサイズを指すものが無いことを、当たった行を1つずつ見て確かめる | - | R1-1 |
| 確かめ方: 書き換えた `claude/CLAUDE.md` の全文と、`localhost の DB につなげるテスト`・`localhost で立てたサイトをブラウザで操作するテスト`・`1つのプロセスの中で、関数の速さを測るテスト` のサイズを聞く文を、`claude -p --model claude-opus-5-5 --setting-sources "" --disable-slash-commands --tools "" --no-session-persistence` の標準入力に渡し、3回とも medium・large・large と答えることを見る。SE の試しは3回ともそう答えた | - | R2-1 |
| 確かめ方: `claude/` を `Software Engineering at Google`・`プロセス`・`localhost`・`1台のマシン` で検索し、分け方が `claude/CLAUDE.md` の1行だけにあることを見る | - | R2-2 |

足した行と直した `claude/` の行は、SE が `ask_rule_line_meaning_in_fresh_sessions.py` に読ませた(2026-11-24)。どの行も、3つのセッションが同じ意味に読み、書いた意図と合った。`small` などがテストサイズだと分からないと3つが答えた2行(3 と、5 の large の行)は「のテスト」を足して読ませ直し、合った。

### サブタスクの前提

## 実装

## レビュー

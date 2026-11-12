# 0072-test-size-labels

ステータス: 設計レビュー中
PC: Reo-Desktop

## 進捗

- 利用者待ち: なし
- [x] 1. やり方を決める(完了条件: 設計の節に、中にする7つのファイルと移すクラス、CLAUDE.md の行が文のまま書いてあり、ADR 0072-1 を書いた。7つ・行3つ・ADR 1件)
- [ ] 2. やり方を見直す(依存: 1)(完了条件: レビューの節の設計への指摘が0件で、ADR 0072-1 が採用になった)
- [ ] 3. 中のテストに印を付ける(依存: 2)(完了条件: 小と中を流すコマンドで 112 件が通り、`tests/` の `medium_test_` で始まるファイルが7つ)
- [ ] 4. 小だけを流すと、ファイルと git を使わないテストだけが流れる(依存: 3)(完了条件: 小だけを流すコマンドで 44 件が通り、`tests/test_*.py` にファイルとほかのプロセスを使う行が0件)
- [ ] 5. CLAUDE.md と README に流し方を書く(依存: 3)(完了条件: リポジトリ直下の CLAUDE.md に、小だけ・小と中・大の流し方の行があり、「テストは小だけ」が0件)
- [ ] 6. できたものを見直す(依存: 3・4・5)(完了条件: レビューの節の実装の指摘が0件)

## 難しさ

- SE: 高(ADR 0067-1 のとおり、いつも高)
- PG: 低(移すクラス・ファイル名・書く行は、設計の節に文のまま書いてある。残るのは、ファイルの頭の import と定義のうち、どれを写し、どれを消すかだけ。ADR 0070-2 のとおり Sonnet 5.5 の high)
- QA: 高(設計レビューで、ADR 0072-1 が全体の既定(ADR 0009-2)から外れる理由が足りているかと、捨てた案より良いかを見る、枠を決める仕事のレビュー。Fable の3つの特徴のうち、利用者が中身を確かめられない分野の知識も、つながった決定も無いので、Opus)

## ゴール

`tests/` のうち、ファイル・git・ほかのプロセスを使うテストに中の印が付いていて、リポジトリ直下の CLAUDE.md の大きさの書き方と、小だけ・小と中を流すコマンドが、テストの実際の大きさに合っている。

なぜ: 全体の CLAUDE.md の ADR 0009-1 では、ファイルに触るテストは中。リポジトリの CLAUDE.md はそれらを小と呼んでいて、目的に反する決まりになっている。0071 の SE が見つけた。

範囲外: テストの中身(クラスとテストのメソッドの中)と、テストが確かめる hooks の動き。全体の CLAUDE.md の「ファイル名に `.medium` を入れる」の行(Python で使えないことは PL に知らせる)。

## 受け入れ条件

1. 小だけを流すコマンドは、ファイル・git・ほかのプロセスを使うテストを流さない。
2. 小と中を流すコマンドは、分ける前と同じ 112 件のテストを流す。
3. 中のテストは、ファイル名が `medium_test_` で始まる。
4. リポジトリ直下の CLAUDE.md に、小だけ・小と中・大を流すコマンドがある。

## 設計

### 読んだ ADR

- 0009-1・0009-2・0009-3(全体の CLAUDE.md の、テストの大きさの見出しに付いた番号)。
- 0011-2(検証コマンドの一覧 `.claude/verify-commands.txt`。プレフィックスは `python -m unittest` のままで、新しいコマンドもみな数えられる)。
- 書き換えるリポジトリ直下の CLAUDE.md の2行目と3行目、`tests/` のファイル、README の行には、ADR の番号が付いていない。仕様(`docs/specs/`)に、テストのファイル名を書いた所は無い。

### 大きさの分け方

- ADR 0009-1 のとおり、テストかテストが呼ぶコードが、ファイルを読み書きするか、git などほかのプロセスを走らせるか、待つ(sleep)なら中。
- テストするモジュールを `importlib` で読み込むのは、コードを読み込む仕組みなので、大きさに数えない。
- 印は、ADR 0072-1 のとおり、ファイル名の頭の `medium_`。中と小が混ざったファイルは、クラスごとに分ける。クラスとテストのメソッドの中は変えない。

### ファイルごとの作業(する人: PG)

名前を変えるだけのファイルは、`git mv` で変える。

| 今のファイル | 中にするもの | 中のファイル | 小に残るクラス | 件数(小 / 中) | 使う資源 |
|---|---|---|---|---|---|
| `test_add_messaging_skill_to_team_roles.py` | 全部 | `medium_test_add_messaging_skill_to_team_roles.py` | なし(元のファイルは無くなる) | 0 / 4 | 一時ファイル |
| `test_ask_about_written_lines.py` | 全部 | `medium_test_ask_about_written_lines.py` | なし(同上) | 0 / 13 | 一時ファイル・git・ほかのプロセス |
| `test_check_rule_documents_changed_by_shell.py` | クラス `コマンドの前後の動き` | `medium_test_check_rule_documents_changed_by_shell.py` | `取り込むgitコマンド`・`取り込んだ行` | 5 / 25 | 一時ファイル・git・ほかのプロセス |
| `test_check_rule_length.py` | クラス `保存したときの動き`・`gitの外と中にまだ無いファイル`・`自動メモリ` | `medium_test_check_rule_length.py` | `決まりの1行の字数`・`プロンプト` | 7 / 13 | 一時ファイル・git・ほかのプロセス |
| `test_require_verify_before_stop.py` | クラス `検証の状態ファイルのロック`・`フックを走らせる` | `medium_test_require_verify_before_stop.py` | `検証コマンドの一覧`・`検証として数えるコマンド`・`止めるかどうか`・`検証の状態ファイルの件数` | 11 / 11 | 一時ファイル・git・ほかのプロセス・待ち |
| `test_skill_md_bullet_length.py` | 全部 | `medium_test_skill_md_bullet_length.py` | なし(同上) | 0 / 1 | リポジトリのファイル |
| `test_team_kanban_fields.py` | 全部 | `medium_test_team_kanban_fields.py` | なし(同上) | 0 / 1 | リポジトリのファイル |

- 変えない小のファイルは、`test_block_history_erasing_push.py`(4件)・`test_push_after_ticket_commit.py`(14件)・`test_remind_pin_after_starting_se.py`(3件)。
- クラスを移すファイルでは、クラスを元の順のまま中のファイルへ移す。
- ファイルの頭の import・定数・関数・テストするモジュールの読み込みは、移したクラスが使うものを中のファイルに写し、小に残るクラスが使わなくなったものは小のファイルから消す。
- 小のファイルには、`tempfile`・`subprocess`・`read_text`・`write_text`・`write_bytes`・`open(`・`.glob(` が残らない。
- 中のファイルの docstring は、1行目(何のテストか)と「仕様は …」の行を残し、「実行(この階層で): 」の行を `python -m unittest discover -s tests -p "*test_*.py"` に直し、その前に「<表の使う資源>を使うので中。」の1行を置く。
- `medium_test_add_messaging_skill_to_team_roles.py` の docstring の「1つのプロセスのメモリと一時ファイルだけなので小。」は、「一時ファイルを使うので中。」に直す。

### リポジトリ直下の CLAUDE.md(する人: PG)

2行目「テストは小だけで、…中と大のテストは無い。」を、次の3行に替える。3行目(変えた所のテストだけ)は、そのまま残す。

```
- 中のテストは、ファイル名の頭に `medium_` を付ける。印の無いテストは小。(ADR 0072-1)
- 小だけは、リポジトリのルートで `python -m unittest discover -s tests`。
- 小と中は、`python -m unittest discover -s tests -p "*test_*.py"`。大のテストは無い。
```

### README(する人: PG)

構成の図の `tests/` の行の括弧を、`(hooks と skill のテスト。流し方はリポジトリ直下の CLAUDE.md)` に替える。コマンドを2か所に書かないため。

### テスト一覧

テストは作らない(テストのファイルを分け、名前を変えるだけで、確かめる動きは変わらない)。確かめ方は次のとおり。

| 確かめ方 | 大きさ | 受け入れ条件 |
|---|---|---|
| `python -m unittest discover -s tests` が 44 件で OK | 小 | 1 |
| `grep -nE "tempfile\|subprocess\|read_text\|write_text\|write_bytes\|open\(\|\.glob\(" tests/test_*.py` が0件 | 確かめ方 | 1 |
| `python -m unittest discover -s tests -p "*test_*.py"` が 112 件で OK | 小と中 | 2 |
| `tests/medium_test_*.py` が7つで、ファイルごとの件数が上の表の中の件数のとおり(`python -m unittest tests/<ファイル>.py` で数える) | 中 | 2・3 |
| リポジトリ直下の CLAUDE.md に、上の3行があり、「テストは小だけ」が0件 | 確かめ方 | 4 |

## 実装

## レビュー

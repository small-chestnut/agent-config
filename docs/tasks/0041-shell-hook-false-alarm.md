ステータス: 実装レビュー済み

## 進み具合

- 利用者待ち: なし
- [x] 1. やり方を決める(済んだ印: ADR 1件・仕様の3行・テスト一覧の28件がある)
- [x] 2. やり方を見直す(前: 1)(済んだ印: レビューの節に設計レビューの指摘が5件ある)
- [x] 3. ほかのセッションが Edit・Write・MultiEdit で書いた行を、シェルのフックが知らせない(前: 2)(済んだ印: テスト一覧の新しい7件が通り、全体81件が通った)
- [x] 4. このフックの 10/31 より前のテスト11件を見直す(前: 2)(済んだ印: テストが22件から28件になり、6件を消し、5件を中のテストに書き直した)
- [x] 5. できたものを見直す(前: 3・4)(済んだ印: レビューの節に実装レビューの指摘が1件ある)

## ゴール

- シェルのフックが、そのコマンドで足していない行(ほかのセッションかほかの呼び出しが Edit・Write・MultiEdit で書いた行)を、「このコマンドでプロンプトに足した行です」と知らせない。
- このフックのテストのうち、2026-10-31 より前に作ったものが、今のテストの決まりに合っている。
- 範囲外: ほかのフックの動きと、2026-10-31 以後に作ったテスト。

### 起きたことの原因(確かめた事実)

- PL のコマンドは `cd "<0038 の worktree>"` を含むので、フックはその worktree も写しに取った。
- 0038 の commit `71aed60`(18:54:17)と `264a733`(18:55:27)の間に、0038 の PG が `claude/CLAUDE.md` の132行目の見出しを書き換えた。PL の言う 09:54 を UTC と読むと、18:54 JST で重なる。
- `264a733` で変わった3行(132・135・138行目)のうち、知らせに出たのは132行目だけ。1行ずつ書く Edit の書き方に合う。
- フックは「写しとコマンドの後の差」を全部そのコマンドのものとするので、コマンドの間にほかのセッションが書いた行も知らせた。

## 受け入れ条件

1. Edit・Write・MultiEdit がそのファイルに書いた行と同じ行は、足した行に数えない。
2. Edit・Write・MultiEdit では、フックは知らせず、書き込みを止めない。
3. このフックのテストのうち 2026-10-31 より前に作った11件が、テスト一覧の「見直し」のとおりに、残す・消す・書き直すのどれかになっている。

## 設計

### 直すファイル

| ファイル | 直すこと |
|---|---|
| `claude/hooks/check_rule_documents_changed_by_shell.py` | 引数 `record` と `confirm` の動きを足す。after で、書けた記録の行を足した行から除く。`remove_old_snapshots` が `written/` の記録も消すようにする。冒頭の docstring に record・confirm の行を足し、その行の末尾に「(ADR 0041-1)」を付ける |
| `claude/user-settings.json` | `hooks.PreToolUse` に、matcher `Edit\|Write\|MultiEdit` の項を足し、このフックを `record` で呼ぶ。`hooks.PostToolUse` の matcher `Edit\|Write\|MultiEdit` の項に、このフックを `confirm` で呼ぶ行を足す(書き方は今の before の行と同じ) |
| `docs/specs/check_rule_documents_changed_by_shell.py.md` | 設計のコミットで直した(ADR の節と、受け入れ条件1・2の行) |
| `.claude/rules/hooks.md` | 下の「なぜ」の見出しと2行を足す |
| `tests/test_check_rule_documents_changed_by_shell.py` | テスト一覧のとおり |

### record の動き(PreToolUse の Edit・Write・MultiEdit)

- `tool_input.file_path` がプロンプトでなければ、何もしない。プロンプトかは、ファイルがまだ無くても決まるように、次の3つで決める。
  - `repository_root(file_path の親)` で git リポジトリの中にある。
  - ルートからのパスが `is_rule_document(rel, patterns)` に当たる(patterns は `rule_documents` と同じく `.claude/rule-documents.txt` から)。
  - `git check-ignore -q -- <rel>` が当たらない(git が無視するファイルではない)。
- 書いた後の中身を、今の中身から作る。
  - Edit: 今の中身の `old_string` を、すべて `new_string` に置き換える(Claude Code は `replace_all` でなければ1か所しか無いときだけ書くので、書けたときはすべて置き換えて同じ結果になる)。
  - MultiEdit: `edits` を上から順に、Edit と同じく当てる。
  - Write: `content`。
  - ファイルが無ければ、今の中身は空。`old_string` が見つからなければ、何も記録しない。
- `added_lines(今の中身, 書いた後の中身)` の行の文字列を、書きかけの記録に書く。
- 何があっても exit 0、stderr には何も出さない(例外も 0)。

### confirm の動き(PostToolUse の Edit・Write・MultiEdit)

- 同じ呼び出し(`session_id` と `tool_use_id`)の書きかけの記録があれば、書けた記録に名前を替える。無ければ何もしない。
- PostToolUse は書けた呼び出しにだけ来るので、拒まれた・失敗した呼び出しの記録は書きかけのまま残り、after は使わない。
- 何があっても exit 0、stderr には何も出さない(例外も 0)。

### 記録(データ)

- 置き場: `SNAPSHOT_DIR / "written"`。
- 1つの呼び出しに1つの JSON ファイル。名前の頭は `<ファイルのパスの sha256 の頭16字>-<session_id:tool_use_id の sha256 の頭16字>`。
- 書きかけの記録は `<頭>.pending.json`、書けた記録は `<頭>.json`。
- ファイルのパスは `os.path.normcase(str(Path(file_path).resolve()))`。
- 中身は `{"lines": [行の文字列, …]}`。
- before の `remove_old_snapshots` が、写しと同じく、1日たった記録(書きかけも書けたものも)を消す。

### after の除き方

- `findings` で、取り込んだ行を除いた後に、そのファイルのパスの頭16字で始まる書けた記録(`.pending.json` でないもの)をすべて読み、記録の行と同じ文字列の行を `new_lines` から除く。
- 除くのは、同じファイルの記録の行だけ。
- どのセッションの記録かは問わない(自分のセッションの Edit の行も、書いたときに問われている)。

### hooks.md に足す「なぜ」

`### 目指す状態: 取り込んだだけの決まりの行を、Claude に書き換えさせない` の節の後に:

```
### 目指す状態: ほかの呼び出しが書いた行を、シェルの行として直させない

- Edit・Write・MultiEdit が書いた行は、シェルの後に問わない。(ADR 0041-1)
- ほかのセッションの行を直しに行くと、その作業とぶつかる。
```

### テスト一覧

大きさの印(`.medium`)は付けない。このファイルは小と中が混ざっており、ファイルを分けるのは既にあるファイルの形を直す別の変更。

「中」のテストは、今の `コマンドの前後の動き` の組み立て(一時的な git リポジトリで、フックを before・after として走らせる)を使う。record と confirm は、`tool_name` が `Edit` などで、`session_id` と `tool_use_id` が before と違う event でフックを走らせる。書けた呼び出しは、record → ファイルを書き換える → confirm の順に走らせる。

#### 足すテスト

| テスト名 | 大きさ | 受け入れ条件・作る規則 |
|---|---|---|
| test_コマンドの間にEditで足された行は問わない | 中 | 1・バグの再現(before → record(Edit)→ Edit と同じ書き換え → confirm → after が exit 0) |
| test_コマンドで足した行はEditで足された行と並んでも問う | 中 | 1(除くのは記録した行だけ。Edit の行とコマンドの長い行を足し、after がコマンドの行だけを出す) |
| test_Writeで作られたプロンプトの行は問わない | 中 | 1・Write とファイルが無いときの分かれ目 |
| test_MultiEditで書かれた行は問わない | 中 | 1・MultiEdit の分かれ目 |
| test_別のファイルにEditで書かれた行と同じ行をコマンドで足すと問う | 中 | 1・同じファイルの記録だけを除く分かれ目(ファイル A に Edit で長い行を書いて confirm まで済ませ、コマンドでファイル B に同じ行を足すと、after が B の行を出す) |
| test_書けなかったEditの行はコマンドで足すと問う | 中 | 1・書けた呼び出しだけを除く分かれ目(record だけで confirm の無い Edit の行を、コマンドで足すと、after がその行を出す) |
| test_EditWriteMultiEditでは知らせず書き込みを止めない | 中 | 2(長い行を足す Edit の record と confirm が、どちらも exit 0、stderr が空) |

#### 見直し(2026-10-31 より前に作った11件)

今の決まり「テストは、外から呼べる入口で呼び、外から見える結果を確かめる」で、このフックの入口は、フックを before・after として走らせること。部品(関数)だけを呼ぶ6件は内部の作りのテストなので消し、その分かれ目を確かめるテストがほかに無いものは、入口から確かめる中のテストに書き直す。

| 今のテスト名 | 決めたこと | 理由 |
|---|---|---|
| test_ドライブ文字のパスを拾う | 消す | 部品だけを呼ぶ。中のテストはみな `cd "C:/…"` で走るので、同じ分かれ目を既に通っている |
| test_Git_Bash_の形のパスをドライブ文字に直す | 書き直す → test_Git_Bashの形のパスのリポジトリも見る(中) | 部品だけを呼ぶ。`/c/…` の分かれ目は、ほかに確かめるテストが無い。ドライブ文字の無い環境では飛ばす |
| test_ホームからのパスを拾う | 書き直す → test_ホームからのパスのリポジトリも見る(中) | 同上(`~/…`)。一時フォルダがホームの下に無い環境では飛ばす |
| test_足した行と書き換えた行の番号を返す | 書き直す → test_コマンドで書き換えた行も問う(中) | 部品だけを呼ぶ。足した行は test_コマンドで長い決まりを足すと知らせと問いが返る が確かめているので、書き換えた行だけを書き直す |
| test_消しただけなら足された行は無い | 書き直す → test_コマンドで消しただけなら問わない(中) | 部品だけを呼ぶ。仕様の「消しただけの行は数えない」を入口から確かめるテストが無い |
| test_コードブロックの中と空の行は問わない | 書き直す → test_空の行とコードブロックの中は問わない(中) | 部品だけを呼ぶ。コードブロックの中は短い行にして、字数の知らせが出ないようにする |
| test_コマンドで長い決まりを足すと知らせと問いが返る | 残す | 仕様の「知らせる」の2行と exit 2 を入口から確かめる |
| test_コマンドの前からあった変更は問わない | 残す | 仕様の「コマンドの前から作業ツリーにあった変更」の分かれ目 |
| test_コマンドで作ったプロンプトも数える | 残す | 仕様の「コマンドで作ったプロンプト」の分かれ目 |
| test_プロンプトでなければ問わない | 残す | このフックがプロンプトだけを見る分かれ目(何がプロンプトかの規則は test_check_rule_length.py が確かめる。こちらはその規則を使うかを確かめる) |
| test_写しが無ければ何もしない | 残す | 仕様の「写しが無ければ何もしない」の分かれ目 |

#### 確かめ方(テストでないもの)

| 変更 | 確かめ方 |
|---|---|
| `claude/user-settings.json` | `python -c "import json;json.load(open('claude/user-settings.json',encoding='utf-8'))"` が通り、matcher `Edit\|Write\|MultiEdit` の項に、`hooks.PreToolUse` では `check_rule_documents_changed_by_shell.py" record`、`hooks.PostToolUse` では `check_rule_documents_changed_by_shell.py" confirm` の行が1つずつある |
| `.claude/rules/hooks.md` | 上の見出しと2行がある |

テストの数: このファイルは今22件。消す6件・足す12件(新しい7件・書き直した5件)で28件。

## 実装

- フック: `claude/hooks/check_rule_documents_changed_by_shell.py` に `record`・`confirm` と、after で書けた記録の行を除く処理、`remove_old_snapshots` の `written/` 対応、冒頭の docstring の行(ADR 0041-1)を足した。
- 設定: `claude/user-settings.json` の `hooks.PreToolUse` に `record`、`hooks.PostToolUse` の `Edit|Write|MultiEdit` に `confirm` を足した。`json.load` が通り、2行が1つずつある。
- 「なぜ」: `.claude/rules/hooks.md` に見出しと2行を足した。
- テスト: `tests/test_check_rule_documents_changed_by_shell.py` は22件から28件(新しい7件・書き直した5件・消した6件)。大きさの印は付けていない(設計のとおり)。
- 実行: `python -m unittest discover -s tests` で81件が通った(スキップ無し)。lint のコマンドはこのリポジトリに無い。
- 設計の決めていない所を判断した所: なし。
- 実装レビュー(1回目)の指摘を直した: `.claude/rule-documents.txt` を読む処理を `project_patterns` にまとめ、`rule_documents` と `is_prompt_file` の両方から呼ぶ。81件が通った。
- 反映: `~/.claude` への `install.ps1 -Yes` は、main にマージした後に PL か利用者が行う(PG はしていない)。

## レビュー

### 設計レビュー(1回目)

- 直すファイルの表に `remove_old_snapshots` が無い。今は `SNAPSHOT_DIR` 直下の `*.json` だけを消すので、`written/` の記録は消えない。表に足す。
- record は PreToolUse で書くので、拒まれた・失敗した Edit(`old_string` が2か所、未読など)の行も記録する。ADR の理由1「見落としにならない」と合わない。理由に、そのときは見落とすと書くか、防ぐ設計にする。
- record の「プロンプトか」を `rule_documents` と同じ決め方とすると、`git ls-files` は無いファイルを返さず、Write で作るプロンプトを記録しない。名前の決め方(`is_rule_document`)と git の無視で決めると書く。
- 足りないテスト: 記録の行を除くのは同じファイルだけ、という分かれ目(仕様の「そのファイルに書いた行」)。別のファイルに Edit で書いた行と同じ行をコマンドで足すと問う、のテストを足す。
- ADR 0041-1 の番号をコードのどこに付けるかが無い。`require_verify_before_stop.py` と同じく、冒頭の docstring の record の行に「(ADR 0041-1)」を付ける設計にする。
- ADR 0041-1 は、指摘2があるので「提案」のまま。
- テスト一覧の「見直し」11件は、10/22 の `b238a0b` で作った11件と合い、決めたことはテストの基準に合っている。

### 実装レビュー(1回目)

- `is_prompt_file` が `.claude/rule-documents.txt` を読む2行は、`rule_documents` と同じ。片方だけ直すと record と after でプロンプトの決め方がずれるので、1つの関数にまとめて両方から呼ぶ。
- テストは、28件(新しい7件・書き直した5件・残した古い5件・範囲外の 10/31 以後の11件)で、テスト一覧と名前が合い、消した6件は無い。
- ADR 0041-1 の番号は、docstring の record の行と `.claude/rules/hooks.md` の行にあり、仕様の「ADR」の節にもある。
- 動きは仕様の行と合っている。

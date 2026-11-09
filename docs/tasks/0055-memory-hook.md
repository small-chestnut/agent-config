# 0055-memory-hook

ステータス: 設計中

## 進捗

- 利用者待ち: なし
- [/] 1. やり方を決める(完了条件: 設計の節と ADR 2件をコミットした)
- [ ] 2. やり方を見直す(依存: 1)(完了条件: レビューの節に設計レビューの結果が1件ある)
- [ ] 3. 自動メモリに書いた行にも、字数の数えと問いが掛かる(依存: 2)(完了条件: テスト一覧の 1〜7 が通る)
- [ ] 4. 書いた行の問いに、例の並びの問いが入る(シェルで書いた行も)(依存: 2)(完了条件: テスト一覧の 8〜10 が通る)
- [ ] 5. できたものを見直す(依存: 3・4)(完了条件: レビューの節に実装レビューの結果が1件ある)

## ゴール

Claude が自動メモリ(会話をまたいで残すメモの md)を書く・直すときにも、プロンプトと同じフックが、書いた行の字数を数え、書いた行を問い返す。問い返しには、消せる語に加えて、決まりを1文の状態で言わずに具体例を並べている所が入る。

なぜ: 具体例は書いた例にしか効かず、書いていない場面は構わないと読まれる。その穴を例で塞ぐと規則の束ができ、コンテキストが膨らむ。決まりは、例がみなそこから出てくる状態を1文で言う。決まりの文書は利用者とフックが見ているが、メモリは Claude が一人で書き、誰も読み返さず、フックも掛かっていない。利用者は、Claude がこの傾向を抑える仕組みを自分で持つことを求めている。

範囲外: シェル(Bash・PowerShell)で書いた自動メモリ、全体の CLAUDE.md と prompt-structure の規則の書き換え、既にある自動メモリの中身の書き換え。

## 受け入れ条件

1. 自動メモリに足した長い決まりの行は、行番号を並べて Claude に返る。
2. 自動メモリの、この保存で書いていない行は、長くても知らせない。
3. 設定ディレクトリの `projects/*/memory/` の外の md は、自動メモリとして数えない。
4. `CLAUDE_CONFIG_DIR` が無いときは、`~/.claude` の自動メモリを数える。
5. リンク `[文](先)` は、文だけを数える。
6. 自動メモリでも、この保存で書いた行だけを問う。
7. 自動メモリでない、git の外のファイルは、今のとおり数えず問わない。
8. 書いた行の知らせは、消せる語と、具体例を並べている所の2つを問う。
9. シェルで足したプロンプトの行の知らせも、同じ2つを問う。
10. 問いの文は、`ask_about_written_lines.py` の1か所にだけある。
11. `ask_removable_words.py` の名前は、リポジトリのどこにも残っていない(ADR を除く)。
12. `python -m unittest discover -s tests` が全部通る。

## 設計

### 書き換える行と、付いた ADR

| ファイル | 書き換える所 | 付いた ADR |
|---|---|---|
| `claude/hooks/check_rule_length.py` | プロンプトの読み方・字数の数え方 | なし |
| `claude/hooks/ask_removable_words.py` | 名前と知らせの文 | なし |
| `claude/hooks/check_rule_documents_changed_by_shell.py` | 問いの知らせの文 | 0041-1(書き換える所には効かない) |
| `claude/user-settings.json` | PostToolUse の Edit・Write・MultiEdit のフックの行 | なし |
| `docs/specs/` の3つの仕様 | 下の「仕様」 | なし |
| `.claude/rules/hooks.md` | `ask_removable_words.py` の目指す状態 | なし |

読んだ ADR は 0041-1 だけ(書き換える所に効かないので、守ることは無い)。決定は ADR 0055-1(自動メモリにも掛ける)と 0055-2(例の問いを同じ知らせに入れ、名前を替える)に、状態「提案」で書いた。

### 全体の CLAUDE.md と prompt-structure に規則を足さない

- prompt-structure には既に「プロンプトは、一般の文だけで書く」(0027 で「例は置かない」から言い換えた行)があり、親の目的「AI が、規則に無いことでも、利用者の意図どおりに動けるようにする」と、その skill の CLAUDE.md の「規則が、止めたいものの数だけ増えず、書き漏らしたものも止める」が、例を並べない理由を既に言っている。
- それでも例が並ぶのは、規則が足りないからではなく、書いている最中に気づかないから。メモリを書くときには prompt-structure は読み込まれない。書いたその場で問い返すフックが、その抜けを埋める。
- だから、全体の CLAUDE.md と prompt-structure は変えない。

### 自動メモリの見分け方(`check_rule_length.py`)

- 設定ディレクトリは、環境変数 `CLAUDE_CONFIG_DIR` が空でなければそれ、無ければ `Path.home() / ".claude"`。
- 自動メモリは、`<設定ディレクトリ>/projects/<1段>/memory/` の下にある、拡張子 `.md` のファイル。
- 比べるパスは `os.path.abspath` と `os.path.normcase` を掛けたもので、リンク(ジャンクション)はたどらない。`~/.claude-work` の `projects` の下にはジャンクションがあり、たどると別の設定ディレクトリのパスになるため。
- 関数 `is_memory(path: Path) -> bool` を足す。

### 自動メモリの足した行(`check_rule_length.py`)

- git の差分の代わりに、この保存で書いた文字列を使う。足した行は、書いた文字列の空でない1行(前後の空白を除く)を1つでも含む行。
- 書いた文字列を取る `written_text(tool_input)` を、`ask_removable_words.py` から `check_rule_length.py` へ移す(中身は今のまま)。
- 関数 `written_line_numbers(text: str, written: str) -> set[int]` を足す。
- `read_rule_document(path, written)` は、書いた文字列を2つ目の引数で受け取る。自動メモリなら、git を見る前に `(path.as_posix(), 中身, written_line_numbers(中身, written))` を返す。自動メモリでなければ今のまま。
- `check(path, tool_input)` と `main()` は、`tool_input` を渡す。

### リンクの字数(`check_rule_length.py`)

- `rule_length` は、`` `…` `` を1字に替えた後、`[文](先)` を `文` に替えて数える。正規表現は `\[([^\]]*)\]\([^)]*\)`。
- 自動メモリの索引(`MEMORY.md`)の1行はリンクで始まり、行き先のファイル名まで数えると、中身を書く字数が残らないため。プロンプトの行にも同じに掛かる。

### 書いた行を問うフックの名前と問い(`ask_about_written_lines.py`)

- `claude/hooks/ask_removable_words.py` を `git mv` で `claude/hooks/ask_about_written_lines.py` に替える。冒頭の説明も、2つを問うことに直す。
- 問いの文を、モジュールの定数 `QUESTIONS` に置く。中身は次の2行(行頭の2つの空白も含む)。

  ```
    1. 消しても意味が変わらない語は、消す。
    2. 言いたい決まりや事実を1文で言わずに、具体例を並べている所は、例がみなそこから出てくる状態の1文に替える。
  ```

- 知らせは、`この保存で足した行です。行ごとに次の2つを確かめ、当たる所を直してください:` の1行、`QUESTIONS`、問う行の並び(今の形 `  <パス>:<行番号>  <行>`)の順に stderr に出し、exit 2。
- 問う行の決め方(`asked_lines`)は今のまま。`read_rule_document(path, written_text(tool_input))` を呼ぶ。

### シェルで書いた行の問い(`check_rule_documents_changed_by_shell.py`)

- `from ask_about_written_lines import QUESTIONS` を足す。
- 問いの知らせの1行目を `このコマンドでプロンプトに足した行です。行ごとに次の2つを確かめ、当たる所を直してください:` に替え、その次に `QUESTIONS` を出し、その後に今の行の並びを出す。
- 冒頭の説明の `ask_removable_words.py` を `ask_about_written_lines.py` に替える。
- シェルで書いた自動メモリは見ない(範囲外)。Claude Code は自動メモリを Write で書くよう指示しているため。

### 設定(`claude/user-settings.json`)

- PostToolUse の `Edit|Write|MultiEdit` の2つ目のフックの行の `ask_removable_words.py` を `ask_about_written_lines.py` に替える。ほかの行は変えない。
- `claude/project-settings.json` には、このフックの行が無いので変えない。

### なぜのファイル(`.claude/rules/hooks.md`)

「書いている最中には気づけない冗長さ」の目指す状態を、次の2つに置き換える(ADR 番号は付けない。この文書は「なぜ」の置き場なので)。

```
### 目指す状態: 書いている最中には気づけない冗長さと例の並びに、1か所を指して問い返している

- `ask_about_written_lines.py` は、足した行を1か所ずつ指して問い返している。
- 例の並びは、書いた例にしか効かず、穴を例で塞ぐと規則の束ができる。

### 目指す状態: 誰も読み返さない自動メモリにも、プロンプトと同じ数えと問いが掛かっている

- 自動メモリは Claude が一人で書き、利用者もほかのフックも見ていない。
```

### 仕様

- `docs/specs/ask_removable_words.py.md` を `git mv` で `docs/specs/ask_about_written_lines.py.md` に替え、見出しを `# ask_about_written_lines.py` にする。
- `docs/specs/ask_about_written_lines.py.md` の「ADR」の節を `- 0055-1 自動メモリにも、プロンプトの字数の数えと問いを掛ける` と `- 0055-2 例の並びの問いを、消せる語の問いと同じ知らせに入れる` の2行にし、「足した行を問い返す」の節に次の2行を足す。
  - `問いは、消しても意味が変わらない語と、決まりや事実を1文で言わずに具体例を並べている所の2つ。`
  - `自動メモリでは、git の差分の代わりに、この保存で書いた文字列を含む行を足した行とする。`
- `docs/specs/check_rule_length.py.md` の「ADR」の節を `- 0055-1 自動メモリにも、プロンプトの字数の数えと問いを掛ける` にし、次を足す。
  - 「字数の数え方」に `リンク [文](先) は、文だけを数える。`(行の中のリンクの部分はバッククォートで囲む)
  - 新しい節 `## 自動メモリ` に、次の3行。
    - `設定ディレクトリ(CLAUDE_CONFIG_DIR、無ければ ~/.claude)の projects/<プロジェクト>/memory/ の下の md は、自動メモリ。`
    - `自動メモリでは、この保存で書いた文字列を含む決まりの行を、足した行として数える。`
    - `自動メモリのパスは、リンクをたどらずに比べる。`
  - 「プロンプト」の節の `git の外のファイルは数えない。` を `自動メモリのほかの、git の外のファイルは数えない。` に替える。
- `docs/specs/check_rule_documents_changed_by_shell.py.md` の「ADR」の節に `- 0055-2 例の並びの問いを、消せる語の問いと同じ知らせに入れる` を足し、「知らせる」の節の `足した行を、空の行とコードブロックの中を除いて並べ、消しても意味が変わらない語を探すよう問う。` を `足した行を、空の行とコードブロックの中を除いて並べ、ask_about_written_lines.py と同じ2つを問う。` に替える。

仕様の行の中のパスとファイル名は、バッククォートで囲む。

### テストのファイル

- `tests/test_ask_removable_words.py` を `git mv` で `tests/test_ask_about_written_lines.py` に替え、冒頭の説明と `SCRIPT` のパスを新しい名前にする。
- 自動メモリのテストは、`CLAUDE_CONFIG_DIR` を一時フォルダにした環境変数でフックを走らせ、`<一時フォルダ>/projects/p/memory/a.md` を書く。テスト 4 は `CLAUDE_CONFIG_DIR` を消し、`HOME` と `USERPROFILE` を一時フォルダにする。

### テスト一覧

| # | テスト名 | ファイル | 大きさ | 受け入れ条件 |
|---|---|---|---|---|
| 1 | `test_自動メモリに足した長い決まりの行の番号をClaudeに返す` | test_check_rule_length.py | 小 | 1 |
| 2 | `test_自動メモリのこの保存で書いていない長い行は知らせない` | test_check_rule_length.py | 小 | 2 |
| 3 | `test_設定ディレクトリの外のmemoryフォルダのmdは数えない` | test_check_rule_length.py | 小 | 3・7 |
| 4 | `test_CLAUDE_CONFIG_DIRが無ければホームの_claudeの自動メモリを数える` | test_check_rule_length.py | 小 | 4 |
| 5 | `test_リンクは文だけを数え60字までは知らせず61字から知らせる` | test_check_rule_length.py | 小 | 5 |
| 6 | `test_自動メモリでもこの保存で書いた行だけを問う` | test_ask_about_written_lines.py | 小 | 6 |
| 7 | `test_自動メモリでないgitの外のファイルは問わない` | test_ask_about_written_lines.py | 小 | 7 |
| 8 | `test_知らせは消せる語と具体例の並びの2つを問う` | test_ask_about_written_lines.py | 小 | 8 |
| 9 | `test_コマンドで足した行にも同じ2つを問う` | test_check_rule_documents_changed_by_shell.py | 小 | 9 |
| 10 | `test_問いの文はask_about_written_linesの1か所にだけある`(`QUESTIONS` の2行目の文が、`claude/hooks/` の中で `ask_about_written_lines.py` にだけある) | test_ask_about_written_lines.py | 小 | 10 |
| — | `git grep -n ask_removable_words -- ':!docs/adr'` が何も出さない | — | — | 11 |
| — | `python -m unittest discover -s tests` が 81 件 OK | 小 | — | 12 |

テスト 5 は、`[` + 「あ」60 字 + `](x.md)` の行を知らせず、61 字の行を知らせる(境界値分析)。テスト 1・2・6 は Edit の new_string で書いた行を使う。

### マージの後(する人: PL)

- install(`install.ps1 -Yes`)の後、`~/.claude/hooks/ask_removable_words.py` と `~/.claude-work/hooks/ask_removable_words.py` が残る(install は古いファイルを消さない)。どの設定からも呼ばれなくなるので、対象と理由を利用者に伝えてから `trash` で消す。

## 実装

## レビュー

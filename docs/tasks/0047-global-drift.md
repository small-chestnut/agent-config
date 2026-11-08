ステータス: 設計レビュー中

## 進捗

- 利用者待ち: なし
- [x] 1. やり方を決める(完了条件: 設計の節と ADR がコミット済み → 設計の節と ADR 0047-1・0047-2 を提案でコミットした)
- [ ] 2. やり方を見直す(依存: 1)(完了条件: ADR 0047-1・0047-2 の2件の状態が採用)
- [ ] 3. 全体の規則が目的とぶつかったら、その場で目的の方に従う決まりを、全体の CLAUDE.md に足す(依存: 2)(完了条件: 確かめ方 A〜D がどれも1件)
- [ ] 4. install が、その PC の agent-config の場所を書き残すようにする(依存: 2)(完了条件: 中のテスト2件が通るか、その OS で動かないものだけ飛ばされ、確かめ方 K が1件)
- [ ] 5. 気づいたずれを agent-config のチケットにする決まりを、全体の CLAUDE.md に足す(依存: 2)(完了条件: 確かめ方 E〜J がどれも1件)
- [ ] 6. agent-config の PL が、届いたずれを拾ってタスクにする決まりを足す(依存: 2)(完了条件: 確かめ方 L が3件、M・N がどれも1件)
- [ ] 7. できたものを見直す(依存: 3・4・5・6)(完了条件: レビューの節に実装レビューの指摘の件数がある)

## ゴール

ほかのリポジトリで作業中の AI が、全体の CLAUDE.md・skill の規則が目的に反すると気づいたとき、その場では目的の方に従って進め、そのずれを、その PC の agent-config にチケット1つとして足す。agent-config の PL は、届いたずれを聞かずにタスクにして回す。これで、`~/.claude` の写しを直して install で消えることも、気づいたずれが消えることもなく、利用者は矛盾を探して突きつける役を負わずに済む。

範囲外: agent-config の中で気づいたずれの回し方(ADR 0046-3 で決め済み)と、届いたずれを直すタスクの中身と、PC をまたいでチケットを届けること(チケットは、ずれに気づいた PC の agent-config に残る)。

## 受け入れ条件

1. 全体の CLAUDE.md に、全体の CLAUDE.md・skill の規則が、どのリポジトリでも、その親の目的・目指す状態に合うように動いている目指す状態がある。
2. その目指す状態に、全体の規則が親の目的・目指す状態とぶつかったら、目的の方に従う行がある。
3. その目指す状態に、従ったら、どうずれていて、どう動いたかを利用者に伝える行がある。
4. 全体の CLAUDE.md の ADR 0046-3 の目指す状態で、照らす目的と目指す状態を絞る行は、リポジトリの手段を照らす目的と目指す状態は、そのリポジトリの中のものだけ、になっている。
5. 全体の CLAUDE.md に、ほかのリポジトリで気づいた全体の規則のずれが、agent-config のチケットになっている目指す状態がある。
6. その目指す状態に、ずれ1件につき、agent-config に `docs/tasks/drift-<英語の短い名前>.md` を1つ足す行がある。
7. その目指す状態に、agent-config の場所は、設定ディレクトリの `agent-config-path.txt` に書いてある行と、設定ディレクトリは `CLAUDE_CONFIG_DIR` が指す所で、無ければ `~/.claude` である行がある。
8. その目指す状態に、チケットには、規則と目的のファイルと見出し、どうずれているか、どう動いたかを書く行がある。
9. その目指す状態に、作業中のリポジトリのコードとデータは、チケットに写さない行がある。
10. その目指す状態に、場所が分からなければ、チケットの中身を返答で利用者に渡す行がある。
11. install.ps1 は、どの設定ディレクトリにも、agent-config の場所を `agent-config-path.txt` に書く。
12. install.sh は、どの設定ディレクトリにも、agent-config の場所を `agent-config-path.txt` に書く。
13. agent-config の CLAUDE.md に、`docs/tasks/drift-*.md` は、ほかのリポジトリから届いた全体の規則のずれである行がある。
14. agent-config の CLAUDE.md で、PL は、利用者が書いたターンごとに届いたずれを探し、聞かずにタスクにして回す。
15. agent-config の CLAUDE.md で、タスクにした届いたずれのファイルは、利用者に伝えてから消す。
16. agent-config の CLAUDE.md に、小のテスト・中のテスト・大のテストを流すコマンドが1行ずつある。
17. 受け入れ条件 1 と 5 の目指す状態の「なぜ」が `.claude/rules/global-claude-md.md` の原則8 にあり、原則8 の「照らすのはリポジトリの中の目的だけ」の行は、リポジトリの手段を照らすのは、その中の目的だけ、になっている。
18. README のインストールの節に、install が各設定ディレクトリの `agent-config-path.txt` に agent-config の場所を書くことがある。
19. 足した・変えた規則の行は、どれも60字以内。

## 設計

### ADR

- 0047-1 全体の CLAUDE.md・skill の規則が、その親の目的・目指す状態とぶつかったら、どのリポジトリでも目的の方に従い、ずれと動き方を伝える(`docs/adr/0047-1-follow-purpose-over-global-rule.md`、状態: 提案)
- 0047-2 ほかのリポジトリで気づいた全体の規則のずれは、install が書き残した場所の agent-config に、ずれ1件につきチケット1つを足し、agent-config の PL が聞かずにタスクにする(`docs/adr/0047-2-global-drift-ticket.md`、状態: 提案)
- 書き換える行に付いた ADR: `claude/CLAUDE.md` 171 行は見出しの ADR 0046-3。0046-3 の決定(作業するリポジトリの手段を、その中の目的に照らして保つ)は変えず、行の言い方を、リポジトリの手段についての行だと分かるように直すだけなので、置き換えない。リポジトリ直下の `CLAUDE.md` 3 行・`.claude/rules/global-claude-md.md` 113 行・install.ps1・install.sh・README には ADR の番号が無い。足すテストは ADR 0009-2(印の無い道具ではファイル名に `.medium`)と 0005-1 に沿わせた。
- 仕様: 直すのはプロンプトと install。プロンプトはそのまま仕様。install は、用語集のモジュール(skill か hooks のファイル)に当たらないので、仕様を作らない。

### 利用者に聞いて決めたこと

- 渡し先: その PC の agent-config に、ずれ1件につきチケット1つを足す(受け入れ条件 6)。
- 気づいたその場の作業: 規則より、その親の目的の方に従って進める(受け入れ条件 2)。

### 届いたずれのチケットの形

ほかのリポジトリの AI が、agent-config の `docs/tasks/drift-<英語の短い名前>.md` に書く。番号は付けない(番号は PL が振る)。同じ名前があれば、名前の末尾に `-2` のように数字を足す。

```
ステータス: 届いたずれ

## ゴール

<規則のファイルと見出しと行> が、<目的・目指す状態のファイルと見出し> に合っている。
なぜ: <どうずれているか>。その場では <どう動いたか>。
```

agent-config の PL は、このゴールの節をタスクの文として SE に渡し、タスクにしたらこのファイルを、消すことを利用者に伝えてから `trash` で消す(git に入っていないファイルなので、全体の CLAUDE.md 原則1 のとおり)。

### 直すファイルと行

行番号は今の main(27bf760)のもの。どのファイルも作業ツリーの改行は CRLF(git には LF で入る)なので、足す行も周りに合わせる。足す規則の行は、どれも60字以内であることを `check_rule_length.py` の数え方で確かめてある。

#### 作業3: `claude/CLAUDE.md` の原則3(する人: PG)

171 行を次に替える。

```
- リポジトリの手段を照らす目的と目指す状態は、そのリポジトリの中のものだけ。
```

ファイルの最後の行(176 行)の後ろに、空行と次の5行(見出し・空行・規則2行)を足す。

```
### 目指す状態: 全体の CLAUDE.md・skill の規則は、どのリポジトリでも、その親の目的・目指す状態に合うように動いている(ADR 0047-1)

- 全体の規則が親の目的・目指す状態とぶつかったら、目的の方に従っている。
- 従ったら、どうずれていて、どう動いたかを利用者に伝えている。
```

`.claude/rules/global-claude-md.md`:

- 113: `- リポジトリの手段を照らすのは、その中の目的だけ。全体の決まりとは、リポジトリの決まりが勝つ。`
- 原則8 の最後の行(118 行)の後ろに、空行と次の5行を足す(作業5 で、この後ろにさらに足す)。

```
### 目指す状態: 全体の規則も、どのリポジトリでも、その親の目的に従って動く規則になっている

- 利用者は、その場の作業でも、規則より目的の方に従って進めることを選んだ。
- 全体の規則を全体の目的に照らしても、リポジトリの決まりが勝つ向きは変わらない。
```

#### 作業4: install が agent-config の場所を書き残す(する人: PG)

`install.ps1` の `foreach ($dir in $claudeDirs) {` の中、`Install-ConfigFile "$repo\claude\CLAUDE.md" "$dir\CLAUDE.md"` の次に、次の5行を足す。

```
    # Record where this repo is, so a session in another repository can file a
    # ticket here when a global rule conflicts with its purpose.
    $pathFile = "$dir\agent-config-path.txt"
    [System.IO.File]::WriteAllText($pathFile, $repo)
    Write-Host "  recorded: $pathFile"
```

`install.sh` の `for dir in "${claude_dirs[@]}"; do` の中、`install_file "$repo/claude/CLAUDE.md" "$dir/CLAUDE.md"` の次に、次の4行を足す。

```
  # Record where this repo is, so a session in another repository can file a
  # ticket here when a global rule conflicts with its purpose.
  printf '%s\n' "$repo" > "$dir/agent-config-path.txt"
  echo "  recorded: $dir/agent-config-path.txt"
```

`README.md` のインストールの節、37 行(「- 設定は**次のエージェントセッション起動時から**有効」)の後ろに、次の1行を足す。

```
- 各設定ディレクトリの `agent-config-path.txt` に、この agent-config の場所を書く。ほかのリポジトリで全体の規則のずれに気づいた AI が、ここの `docs/tasks/` にチケットを足すのに使う
```

テストを、新しいファイル `tests/test_install_records_repo_path.medium.py` に書く(テスト一覧の 1・2)。install を子プロセスで走らせ、設定ディレクトリを一時フォルダに向ける。

- install.ps1: 環境変数 `USERPROFILE` を一時フォルダにし、その中に `.claude-work` を先に作ってから、`powershell -NoProfile -ExecutionPolicy Bypass -File <リポジトリ>/install.ps1 -Yes` を標準入力なしで走らせる。`.claude` と `.claude-work` の両方の `agent-config-path.txt` の中身(前後の空白を除く)が、リポジトリのルートの絶対パスと同じことを確かめる。Windows で `powershell` があるときだけ走らせ、ほかは飛ばす。
- install.sh: 環境変数 `HOME` を一時フォルダにし、`.claude-work` を先に作ってから、`bash <リポジトリ>/install.sh --yes` を走らせ、同じことを確かめる。Windows では飛ばす(Windows の `bash` は WSL の bash を指すことがあり、パスの形も変わる)。
- ファイルの最後に `if __name__ == "__main__": unittest.main()` を置く。`unittest discover` は名前に `.` が2つあるファイルを読まないので、このファイルは小のテストの実行には入らない。

#### 作業5: `claude/CLAUDE.md` の原則3(する人: PG)

作業3 で足した目指す状態の最後の行の後ろに、空行と次の9行(見出し・空行・規則6行)を足す。

```
### 目指す状態: ほかのリポジトリで気づいた全体の規則のずれは、agent-config のチケットになっている(ADR 0047-2)

- ずれ1件につき、agent-config に `docs/tasks/drift-<英語の短い名前>.md` を1つ足している。
- agent-config の場所は、設定ディレクトリの `agent-config-path.txt` に書いてある。
- 設定ディレクトリは、`CLAUDE_CONFIG_DIR` が指す所で、無ければ `~/.claude`。
- チケットには、規則と目的のファイルと見出し、どうずれているか、どう動いたかを書いている。
- 作業中のリポジトリのコードとデータは、チケットに写していない。
- 場所が分からなければ、チケットの中身を返答で利用者に渡している。
```

足した後の `claude/CLAUDE.md` は 190 行(200 行以内)。

`.claude/rules/global-claude-md.md` の、作業3 で足した目指す状態の最後の行の後ろに、空行と次の6行を足す。

```
### 目指す状態: ほかのリポジトリで気づいた全体の規則のずれが、agent-config に届く規則になっている

- `~/.claude` の写しを直しても、次の install で上書きされて消える。
- agent-config に届かないと、ずれは残り、矛盾を探して突きつける役が利用者に戻る。
- 利用者は、ずれ1件にチケット1つを、その PC の agent-config に足す形を選んだ。
- agent-config は公開のリポジトリで、チケットの文はコミットメッセージや ADR に移る。
```

#### 作業6: リポジトリ直下の `CLAUDE.md`(する人: PG)

3 行を次の3行に替える。

```
- 小のテストは、リポジトリのルートで `python -m unittest discover -s tests`(`.medium` のファイルは読まない)。
- 中のテストは、`python tests/<テストのファイル>.medium.py` で1つずつ流す。小と中は、その両方。
- 大のテストは無い。
```

8 行(「- PL でないセッションは、…」)の後ろに、次の3行を足す。

```
- `docs/tasks/drift-*.md` は、ほかのリポジトリから届いた全体の規則のずれ。(ADR 0047-2)
- PL は、利用者が書いたターンごとにそれを探し、聞かずにタスクにして回す。(ADR 0047-2)
- タスクにした届いたずれのファイルは、利用者に伝えてから消す。
```

`.claude/verify-commands.txt` には中のテストのプレフィックス(`python tests/`)を足さない。足すと、フック `require_verify_before_stop.py` が `python tests/` で始まるどのコマンドも検証と数えるようになり、フックを緩めることになる(全体の CLAUDE.md 原則1。原則3 の「プレフィックスは verify-commands.txt にも」より先)。小のテストのプレフィックス `python -m unittest` は今のまま入っている。

### テスト一覧

| テスト名 | 大きさ | 受け入れ条件 |
|---|---|---|
| 1. `test_install_ps1は_どの設定ディレクトリにも_agent_configの場所を書く` | 中 | 11 |
| 2. `test_install_shは_どの設定ディレクトリにも_agent_configの場所を書く` | 中 | 12 |

2つとも `tests/test_install_records_repo_path.medium.py` の中。中にしたのは、子プロセスを走らせ、ファイルに書くから。分かれ目は設定ディレクトリが1つか2つかだが、`.claude-work` があるときだけ足す動きは今からあるもので、2つあるときに両方へ書くことを確かめれば、1つのときも同じ行が書く。

文書の行は、テストを作らず、次の確かめ方で確かめる(リポジトリのルートで流す)。

| 確かめ方 | 期待 | 受け入れ条件 |
|---|---|---|
| A | 1 | 1 |
| B | 1件 | 2 |
| C | 1件 | 3 |
| D | 1件 | 4 |
| E | 1 | 5 |
| F | 1件 | 6 |
| G | 1件 | 7 |
| H | 1件 | 8 |
| I | 1件 | 9 |
| J | 1件 | 10 |
| K | 1件 | 18 |
| L | 3件 | 13・14 |
| M | 1件 | 15 |
| N | 1件 | 16 |
| O | 1件 | 17 |
| P | 1件 | 17 |
| Q | 何も出ない | 19 |
| R | 全部通る(SKILL.md の箇条書きが60字以内も含む) | 19 |
| S | 1・2 が通る(その OS で動かない方は skipped) | 11・12 |

```
A: grep -c "親の目的・目指す状態に合うように動いている(ADR 0047-1)" claude/CLAUDE.md
B: grep -n "全体の規則が親の目的・目指す状態とぶつかったら、目的の方に従っている" claude/CLAUDE.md
C: grep -n "従ったら、どうずれていて、どう動いたかを利用者に伝えている" claude/CLAUDE.md
D: grep -n "リポジトリの手段を照らす目的と目指す状態は、そのリポジトリの中のものだけ" claude/CLAUDE.md
E: grep -c "agent-config のチケットになっている(ADR 0047-2)" claude/CLAUDE.md
F: grep -n "docs/tasks/drift-<英語の短い名前>.md\` を1つ足している" claude/CLAUDE.md
G: grep -n "agent-config-path.txt\` に書いてある" claude/CLAUDE.md
H: grep -n "規則と目的のファイルと見出し、どうずれているか、どう動いたかを書いている" claude/CLAUDE.md
I: grep -n "コードとデータは、チケットに写していない" claude/CLAUDE.md
J: grep -n "チケットの中身を返答で利用者に渡している" claude/CLAUDE.md
K: grep -n "agent-config-path.txt" README.md
L: grep -n "(ADR 0047-2)\|届いたずれのファイルは" CLAUDE.md
M: grep -n "利用者に伝えてから消す" CLAUDE.md
N: grep -n "大のテストは無い" CLAUDE.md
O: grep -n "リポジトリの手段を照らすのは、その中の目的だけ" .claude/rules/global-claude-md.md
P: grep -n "agent-config に届く規則になっている" .claude/rules/global-claude-md.md
Q: git diff -U0 main -- claude/CLAUDE.md CLAUDE.md .claude/rules/global-claude-md.md | python -c "import sys;sys.path.insert(0,'claude/hooks');import check_rule_length as c;[print(l) for l in sys.stdin.buffer.read().decode('utf-8').splitlines() if l.startswith('+- ') and c.rule_length(l[3:].rstrip(chr(13)))>60]"
R: python -m unittest discover -s tests
S: python tests/test_install_records_repo_path.medium.py -v
```

G は、`設定ディレクトリは、…` の行(受け入れ条件 7 の後半)も目で確かめる。Windows では S の 2 が skipped になるので、install.sh は PG が Git Bash で `t=$(mktemp -d) && mkdir "$t/.claude-work" && HOME="$t" bash -o igncr install.sh --yes && cat "$t/.claude/agent-config-path.txt" "$t/.claude-work/agent-config-path.txt"` を流し(作業ツリーの install.sh は改行が CRLF なので `-o igncr` を付ける。今の install.sh がこの形で最後まで走ることは SE が確かめた)、2つともリポジトリのルートのパス(Git Bash の形 `/c/...`)が出ることを確かめ、実装の節に書く。

## 実装

## レビュー

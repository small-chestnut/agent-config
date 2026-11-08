ステータス: 設計レビュー済み

## 進捗

- 利用者待ち: なし
- [x] 1. やり方を決める(完了条件: 設計の節と ADR がコミット済み → 設計の節と ADR 0047-2(書き直し)・0047-3 を提案でコミットした。0047-1 は採用済み)
- [/] 2. やり方を見直す(依存: 1)(完了条件: ADR 0047-1・0047-2・0047-3 の3件の状態が採用)
- [ ] 3. まだ始めていないタスクを、PL の会話でなくチケットに残す決まりにする(依存: 2)(完了条件: 確かめ方 A〜H・Z がどれも期待どおり)
- [ ] 4. 全体の規則が目的とぶつかったら、その場で目的の方に従う決まりを、全体の CLAUDE.md に足す(依存: 2)(完了条件: 確かめ方 I〜L がどれも期待どおり)
- [ ] 5. install が、その PC の agent-config の本体のフォルダの場所を書き残すようにする(依存: 2)(完了条件: 中のテスト4件が通るか、その OS で動かないものだけ飛ばされ、確かめ方 S・T がどれも1件)
- [ ] 6. 気づいたずれを agent-config のチケットにする決まりを、全体の CLAUDE.md に足す(依存: 2)(完了条件: 確かめ方 M〜R・V がどれも期待どおり)
- [ ] 7. できたものを見直す(依存: 3・4・5・6)(完了条件: レビューの節に実装レビューの指摘の件数がある)

## ゴール

利用者が、やると決めたタスクも、あとで考えたいタスクも、AI の会話の状態によらずチケットで確かめられる。まだ始めていないタスクは、PL の返答の文でなく、ステータス「未着手」か「検討待ち」のチケットとして既定のブランチに残る。ほかのリポジトリで作業中の AI が、全体の CLAUDE.md・skill の規則が目的に反すると気づいたら、その場では目的の方に従って進め、そのずれを agent-config に「未着手」のチケットとして足す。agent-config の PL は、それを既定のブランチにコミットして、ほかのタスクと同じようにチームを起こす。これで、`~/.claude` の写しを直して install で消えることも、気づいたずれを利用者が手で運ぶこともなく、利用者は矛盾を探して突きつける役を負わずに済む。

範囲外: agent-config の中で気づいたずれの回し方(ADR 0046-3 で決め済み)と、届いたずれを直すタスクの中身と、チケットの置き場がファイルでないリポジトリでの、まだ始めていないチケットの置き方(書き方の文書に従う今の決まりのまま)。

## 受け入れ条件

1. skill `task-team-lead` で、起こすまでのタスクは、ステータス「未着手」のチケットにする。
2. skill `task-team-lead` に、まだ始めていないタスクが PL の会話でなくチケットにある目指す状態があり、次の行がある: あとで考えたいタスクはステータス「検討待ち」のチケットにする / まだ始めていないチケットは、番号を振り、ステータスの行とゴールの節だけで作る / ゴールの節にはタスクの文を書く / `small-chestnut` のリポジトリなら既定のブランチにコミットし push する / ほかのリポジトリではコミットせずに既定のブランチの作業ツリーに置く / コミットする前に、その作業ツリーに既定のブランチがチェックアウトされているかを確かめる / されていなければ、コミットせずに置き、利用者に伝える / 利用者が書いたターンごとに、既定のブランチの作業ツリーで番号の無いチケットを探す / 既定のブランチの作業ツリーは `git worktree list` の1行目 / 見つけたチケットは番号を振った名前に変えて、ほかのまだ始めていないチケットと同じに扱う / チームを起こすときは、そのタスクの「未着手」か「検討待ち」のチケットをチームのチケットにする / コミットされていないチケットでチームを起こすときは、SE への prompt にそのパスを添える / チームが動いているタスクのチケットは、ステータスによらず進行中と読む。
3. skill `task-team-lead` で、進捗を聞かれたら、まだ始めていないチケットを、図の後に名前とステータスで1行ずつ並べる。
4. skill `task-team-lead` に、「バックログ」の語が無い(終わったタスクの報告に付ける `/compact` の1行も含む)。
5. skill `task-team-se` で、置き場に「未着手」か「検討待ち」のチケットがあれば、それを直して使い、PL がコミットされていないチケットのパスを添えたら、それを置き場へ移して使う。
6. 全体の CLAUDE.md の原則1 で、作業を作業用のブランチでする行の除外は次の行のチケットを指し、次の行は、既定のブランチに直接コミットするのは、チケットだけのリポジトリと、まだ始めていないチケットである、と言う。
7. 受け入れ条件 2 の目指す状態の「なぜ」が、`claude/skills/task-team-lead/CLAUDE.md` にある。
8. 全体の CLAUDE.md に、全体の CLAUDE.md・skill の規則が、どのリポジトリでも、その親の目的・目指す状態に合うように動いている目指す状態がある。
9. その目指す状態に、全体の規則が親の目的・目指す状態とぶつかったら、目的の方に従う行がある。
10. その目指す状態に、従ったら、どうずれていて、どう動いたかを利用者に伝える行がある。
11. 全体の CLAUDE.md の ADR 0046-3 の目指す状態で、照らす目的と目指す状態を絞る行は、リポジトリの手段を照らす目的と目指す状態は、そのリポジトリの中のものだけ、になっている。
12. 全体の CLAUDE.md に、ほかのリポジトリで気づいた全体の規則のずれが、agent-config のチケットになっている目指す状態がある。
13. その目指す状態に、ずれ1件につき、agent-config に `docs/tasks/<英語の短い名前>.md` を1つ足す行がある。
14. その目指す状態に、agent-config の場所は、設定ディレクトリの `agent-config-path.txt` に書いてある行と、設定ディレクトリは `CLAUDE_CONFIG_DIR` が指す所で、無ければ `~/.claude` である行がある。
15. その目指す状態に、チケットはステータス「未着手」の行とゴールの節だけで書く行と、ゴールの節には、規則と目的のファイルと見出し、どうずれているか、どう動いたかを書く行がある。
16. その目指す状態に、チケットはコミットせずに置き、agent-config の PL に任せる行がある。
17. その目指す状態に、作業中のリポジトリのコードとデータはチケットに写さない行と、場所が分からなければチケットの中身を返答で利用者に渡す行がある。
18. install.ps1 は、worktree から走らせても、どの設定ディレクトリの `agent-config-path.txt` にも、agent-config の本体の作業ツリーの場所を書く。
19. install.ps1 は、git の外から走らせると、install.ps1 のある場所を書く。
20. install.sh は、worktree から走らせても、どの設定ディレクトリの `agent-config-path.txt` にも、agent-config の本体の作業ツリーの場所を書く。
21. install.sh は、git の外から走らせると、install.sh のある場所を書く。
22. agent-config の CLAUDE.md に、小のテスト・中のテスト・大のテストを流すコマンドが1行ずつある。
23. 受け入れ条件 8 と 12 の目指す状態の「なぜ」が `.claude/rules/global-claude-md.md` の原則8 にあり、原則8 の「照らすのはリポジトリの中の目的だけ」の行は、リポジトリの手段を照らすのは、その中の目的だけ、になっている。
24. README のインストールの節に、install が各設定ディレクトリの `agent-config-path.txt` に agent-config の本体の作業ツリーの場所を書くことがある。
25. 足した・変えた規則の行は、どれも60字以内。
26. skill `task-team-lead` で、番号は、main の履歴と既定のブランチの作業ツリーにあるチケットの名前と、進行中のチームの名前の中で、最大の番号の次。

## 設計

### ADR

- 0047-1 全体の CLAUDE.md・skill の規則が、その親の目的・目指す状態とぶつかったら、どのリポジトリでも目的の方に従い、ずれと動き方を伝える(`docs/adr/0047-1-follow-purpose-over-global-rule.md`、状態: 採用)
- 0047-2 ほかのリポジトリで気づいた全体の規則のずれは、install が書き残した agent-config の本体の作業ツリーに、ずれ1件につき「未着手」のチケット1つを、コミットせずに足す(`docs/adr/0047-2-global-drift-ticket.md`、状態: 採用。タスクの文が変わったのと設計レビューの指摘2件で書き直した)
- 0047-3 まだ始めていないタスクは、PL の会話でなく、ステータス「未着手」か「検討待ち」のチケットとして既定のブランチに残す(`docs/adr/0047-3-unstarted-tasks-as-tickets.md`、状態: 提案)
- 書き換える行に付いた ADR:
  - `claude/skills/task-team-lead/SKILL.md` 32・78・95・110 行: 番号なし。見出し(28・74・80・105 行)は、105 行が ADR 0035-1(進捗を図で見せる)で、図は変えず、図の後に1行ずつ並べるだけ。95 行のある見出しの下の 83 行などの ADR 0022-2 は、終わったチケットを作業ブランチで消す決定で、まだ始めていないチケットを既定のブランチに置いても変わらない(チームのチケットになったものは、今どおり作業ブランチで消え、マージで既定のブランチからも消える)。
  - `claude/skills/task-team-se/SKILL.md` 12 行の後ろ: 12 行は ADR 0024-1(置き場は PL が指す)。置き場は変えず、既にあるチケットを使う行を足すだけ。
  - `claude/CLAUDE.md` 13 行: 番号なし。括弧の除外を次の行に移し、まだ始めていないチケットを足す(設計レビュー 2回目の指摘)。171 行は見出しの ADR 0046-3。0046-3 の決定(作業するリポジトリの手段を、その中の目的に照らして保つ)は変えず、行の言い方を、リポジトリの手段についての行だと分かるように直すだけなので、置き換えない。
  - リポジトリ直下の `CLAUDE.md` 3 行・`.claude/rules/global-claude-md.md` 113 行・install.ps1・install.sh・README: 番号なし。
  - 足すテストは ADR 0009-2(印の無い道具ではファイル名に `.medium`)と 0005-1 に沿わせた。
- 仕様: 直すのはプロンプトと install。プロンプトはそのまま仕様。install は、用語集のモジュール(skill か hooks のファイル)に当たらないので、仕様を作らない。

### 利用者に聞いて決めたこと

- ずれの渡し先: agent-config に、ずれ1件につきチケット1つを足す(受け入れ条件 13)。
- 気づいたその場の作業: 規則より、その親の目的の方に従って進める(受け入れ条件 9)。
- まだ始めていないチケットの置き場: 既定のブランチにコミットして push する(受け入れ条件 2・6)。

### まだ始めていないチケットの形

```
ステータス: 未着手

## ゴール

<タスクの文>
```

あとで考えたいタスクは、1行目を `ステータス: 検討待ち` にする。ほかのリポジトリから届くずれのチケットも同じ形で、ゴールの節に、規則と目的のファイルと見出し、どうずれているか、その場でどう動いたかを書く。チームを起こすと、SE がこのチケットに進捗などの節を書き足し、ステータスを「設計中」にする。

### 直すファイルと行

行番号は今の main(27bf760)のもの。どのファイルも作業ツリーの改行は CRLF(git には LF で入る)なので、足す行も周りに合わせる。足す規則の行は、どれも60字以内であることを `check_rule_length.py` の数え方で確かめてある。

#### 作業3: まだ始めていないタスクをチケットに残す(する人: PG)

`claude/skills/task-team-lead/SKILL.md`:

- 32: `- 番号は、main の履歴と既定のブランチの作業ツリーにあるチケットの名前と、進行中のチームの名前の中で、最大の番号の次。`
- 78: `- 起こすまでのタスクは、ステータス「未着手」のチケットにしている。(ADR 0047-3)`
- 79 行(空行)の後ろに、次の15行と空行を足す。

```
### 目指す状態: まだ始めていないタスクは、PL の会話でなくチケットにある(ADR 0047-3)

- あとで考えたいタスクは、ステータス「検討待ち」のチケットにしている。
- まだ始めていないチケットは、番号を振り、ステータスの行とゴールの節だけで作っている。
- ゴールの節には、タスクの文を書いている。
- まだ始めていないチケットは、`small-chestnut` のリポジトリなら既定のブランチにコミットし、push している。
- ほかのリポジトリでは、コミットせずに既定のブランチの作業ツリーに置いている。
- コミットする前に、その作業ツリーに既定のブランチがチェックアウトされているかを確かめている。
- されていなければ、コミットせずに置き、利用者に伝えている。
- 利用者が書いたターンごとに、既定のブランチの作業ツリーで、番号の無いチケットを探している。
- 既定のブランチの作業ツリーは、`git worktree list` の1行目。
- 見つけたチケットは、番号を振った名前に変えて、ほかのまだ始めていないチケットと同じに扱っている。
- チームを起こすときは、そのタスクの「未着手」か「検討待ち」のチケットを、チームのチケットにしている。
- コミットされていないチケットでチームを起こすときは、SE への prompt にそのパスを添えている。
- チームが動いているタスクのチケットは、ステータスによらず進行中と読んでいる。
```

- 95: `` - 報告の最後に、貼って送るだけの1行 `/compact 終わったタスク「<タスク名>」のやりとりは捨てて、進行中のタスクだけ残して` を、コードブロックで付けている。 ``
- 110 行(「- タスクの数とサブタスクは…」)の後ろに、次の1行を足す。

```
- まだ始めていないチケットは、図の後に、名前とステータスを1行ずつ並べている。
```

番号の無いチケットは、ほかのリポジトリから届いたずれのチケット(ADR 0047-2)。PL が作るチケットは作るときに番号を振るので、番号を振ったチケットは次のターンで見つけ直さない。`small-chestnut` 以外が所有するリポジトリでは、コミットされていないチケットは SE の worktree に無いので、SE が置き場へ移す。移すので、チームが終わっても本体の作業ツリーに残らない。

番号は、32 行を直した決まりで振る。既定のブランチにコミットしたまだ始めていないチケットは main の履歴に入り、コミットせずに置いたものは既定のブランチの作業ツリーにあるので、どちらも数に入り、同じ番号が2度振られない(設計レビュー 3回目の指摘)。

`claude/skills/task-team-lead/CLAUDE.md` の 25 行の後ろに、空行と次の6行を足す。

```
### 目指す状態: 利用者は、まだ始めていないタスクを、AI の会話の状態によらず確かめられる

- 利用者は、自分がやりたいことを、AI の会話の状態によらず確かめたい。
- バックログを PL の返答の文に置くと、会話の圧縮の要約に頼って残すことになる。
- Jira や GitHub Issues でも、バックログはまだ始めていないチケットの集まり。
- 既定のブランチに置くのは、どの PC の PL からも見えるようにするため。
```

`claude/skills/task-team-se/SKILL.md` の 12 行の後ろに、次の2行を足す。

```
- 置き場に「未着手」か「検討待ち」のチケットがあれば、それを直して使う。(ADR 0047-3)
- PL がコミットされていないチケットのパスを添えたら、それを置き場へ移して使う。(ADR 0047-3)
```

`claude/CLAUDE.md` の 13 行を、次の2行に替える。

```
- 作業は、既定のブランチではなく、作業用のブランチでしている(次の行のチケットは除く)。
- 既定のブランチに直接コミットするのは、チケットだけのリポジトリと、まだ始めていないチケット。(ADR 0047-3)
```

#### 作業4: `claude/CLAUDE.md` の原則3(する人: PG)

作業3 で1行足した後の行番号で、172 行(今の main の 171 行)を次に替える。

```
- リポジトリの手段を照らす目的と目指す状態は、そのリポジトリの中のものだけ。
```

ファイルの最後の行の後ろに、空行と次の4行(見出し・空行・規則2行)を足す。

```
### 目指す状態: 全体の CLAUDE.md・skill の規則は、どのリポジトリでも、その親の目的・目指す状態に合うように動いている(ADR 0047-1)

- 全体の規則が親の目的・目指す状態とぶつかったら、目的の方に従っている。
- 従ったら、どうずれていて、どう動いたかを利用者に伝えている。
```

`.claude/rules/global-claude-md.md`:

- 113: `- リポジトリの手段を照らすのは、その中の目的だけ。全体の決まりとは、リポジトリの決まりが勝つ。`
- 原則8 の最後の行(118 行)の後ろに、空行と次の4行を足す(作業6 で、この後ろにさらに足す)。

```
### 目指す状態: 全体の規則も、どのリポジトリでも、その親の目的に従って動く規則になっている

- 利用者は、その場の作業でも、規則より目的の方に従って進めることを選んだ。
- 全体の規則を全体の目的に照らしても、リポジトリの決まりが勝つ向きは変わらない。
```

#### 作業5: install が agent-config の本体の作業ツリーの場所を書き残す(する人: PG)

`install.ps1` の `foreach ($dir in $claudeDirs) {`(設定と CLAUDE.md を入れるループ)の前に、次の行を足す。

```
# Record the main working tree of this repo (the first line of `git worktree list`),
# so a session in another repository can file a ticket here when a global rule
# conflicts with its purpose. A worktree is removed after merging, so its path is
# not recorded. Outside git, record where this script is.
$mainTree = $repo
try {
    $first = & git -C $repo worktree list --porcelain | Select-Object -First 1
    if ($first -match '^worktree (.+)$') { $mainTree = $Matches[1] -replace '/', '\' }
} catch {}
```

同じループの中、`Install-ConfigFile "$repo\claude\CLAUDE.md" "$dir\CLAUDE.md"` の次に、次の3行を足す。

```
    $pathFile = "$dir\agent-config-path.txt"
    [System.IO.File]::WriteAllText($pathFile, $mainTree)
    Write-Host "  recorded: $pathFile"
```

git の外で `git` が「not a git repository」で終わっても、標準出力は空なので `$mainTree` は `$repo` のまま。`git` が無ければ `&` が例外を投げ、`catch` で `$repo` のまま。

`install.sh` の `for dir in "${claude_dirs[@]}"; do`(設定と CLAUDE.md を入れるループ)の前に、次の行を足す。

```
# Record the main working tree of this repo (the first line of `git worktree list`),
# so a session in another repository can file a ticket here when a global rule
# conflicts with its purpose. A worktree is removed after merging, so its path is
# not recorded. Outside git, record where this script is.
main_tree="$(git -C "$repo" worktree list --porcelain 2>/dev/null | sed -n '1s/^worktree //p' || true)"
[ -n "$main_tree" ] || main_tree="$repo"
```

同じループの中、`install_file "$repo/claude/CLAUDE.md" "$dir/CLAUDE.md"` の次に、次の2行を足す。

```
  printf '%s\n' "$main_tree" > "$dir/agent-config-path.txt"
  echo "  recorded: $dir/agent-config-path.txt"
```

`README.md` のインストールの節、37 行(「- 設定は**次のエージェントセッション起動時から**有効」)の後ろに、次の1行を足す。

```
- 各設定ディレクトリの `agent-config-path.txt` に、この agent-config の本体の作業ツリー(`git worktree list` の1行目)の場所を書く。ほかのリポジトリで全体の規則のずれに気づいた AI が、そこの `docs/tasks/` にチケットを足すのに使う
```

リポジトリ直下の `CLAUDE.md` の 3 行を、次の3行に替える。

```
- 小のテストは、リポジトリのルートで `python -m unittest discover -s tests`(`.medium` のファイルは読まない)。
- 中のテストは、`python tests/<テストのファイル>.medium.py` で1つずつ流す。小と中は、その両方。
- 大のテストは無い。
```

`.claude/verify-commands.txt` には中のテストのプレフィックス(`python tests/`)を足さない。足すと、フック `require_verify_before_stop.py` が `python tests/` で始まるどのコマンドも検証と数えるようになり、フックを緩めることになる(全体の CLAUDE.md 原則1。原則3 の「プレフィックスは verify-commands.txt にも」より先)。小のテストのプレフィックス `python -m unittest` は今のまま入っている。

テストを、新しいファイル `tests/test_install_records_repo_path.medium.py` に書く(テスト一覧の 1〜4)。install を子プロセスで走らせ、設定ディレクトリを一時フォルダに向ける。

- 期待する本体の作業ツリー: `git -C <リポジトリのルート> worktree list --porcelain` の1行目から `worktree ` を除いたもの。比べるときは、両方を `os.path.normcase(os.path.realpath(...))` にそろえる(Windows では `/` と `\`、大文字と小文字が混ざるため)。テストはふつう worktree から流れるので、1・3 は worktree から走らせた場合を確かめる。
- install.ps1(1・2): 環境変数 `USERPROFILE` を一時フォルダにし、その中に `.claude-work` を先に作ってから、`powershell -NoProfile -ExecutionPolicy Bypass -File <install.ps1> -Yes` を標準入力なし(`stdin=subprocess.DEVNULL`)で走らせ、`.claude` と `.claude-work` の両方の `agent-config-path.txt` の中身(前後の空白を除く)を確かめる。1 はリポジトリの install.ps1 を走らせ、期待する本体の作業ツリーと同じこと。2 は、別の一時フォルダ(git の外)に `install.ps1` と `claude/` を写して走らせ、その一時フォルダと同じこと。Windows で `powershell` があるときだけ走らせ、ほかは飛ばす。
- install.sh(3・4): 環境変数 `HOME` を一時フォルダにし、`.claude-work` を先に作ってから `bash <install.sh> --yes` を走らせ、同じことを確かめる。Windows では飛ばす(Windows の `bash` は WSL の bash を指すことがあり、作業ツリーの install.sh は改行が CRLF になる)。
- ファイルの最後に `if __name__ == "__main__": unittest.main()` を置く。`unittest discover` は名前に `.` が2つあるファイルを読まない(`unittest.loader.VALID_MODULE_NAME` に合わない)ので、このファイルは小のテストの実行には入らない。

#### 作業6: `claude/CLAUDE.md` の原則3(する人: PG)

作業4 で足した目指す状態の最後の行の後ろに、空行と次の10行(見出し・空行・規則8行)を足す。

```
### 目指す状態: ほかのリポジトリで気づいた全体の規則のずれは、agent-config のチケットになっている(ADR 0047-2)

- ずれ1件につき、agent-config に `docs/tasks/<英語の短い名前>.md` を1つ足している。
- agent-config の場所は、設定ディレクトリの `agent-config-path.txt` に書いてある。
- 設定ディレクトリは、`CLAUDE_CONFIG_DIR` が指す所で、無ければ `~/.claude`。
- チケットは、ステータス「未着手」の行と、ゴールの節だけで書いている。
- ゴールの節には、規則と目的のファイルと見出し、どうずれているか、どう動いたかを書いている。
- チケットはコミットせずに置き、agent-config の PL に任せている。
- 作業中のリポジトリのコードとデータは、チケットに写していない。
- 場所が分からなければ、チケットの中身を返答で利用者に渡している。
```

足した後の `claude/CLAUDE.md` は 193 行(200 行以内)。

`.claude/rules/global-claude-md.md` の、作業4 で足した目指す状態の最後の行の後ろに、空行と次の7行を足す。

```
### 目指す状態: ほかのリポジトリで気づいた全体の規則のずれが、agent-config に届く規則になっている

- `~/.claude` の写しを直しても、次の install で上書きされて消える。
- agent-config に届かないと、ずれは残り、矛盾を探して突きつける役が利用者に戻る。
- 利用者は、ずれ1件にチケット1つを、agent-config に足す形を選んだ。
- ほかのリポジトリの会話が agent-config の git を動かすと、PL の作業とぶつかる。
- agent-config は公開のリポジトリで、チケットは既定のブランチに push される。
```

届いたずれのチケットを拾ってチームを起こすのは、作業3 で足す skill `task-team-lead` の行(既定のブランチの作業ツリーで、コミットされていないチケットを探す)と、agent-config の CLAUDE.md の今の行(目的に反する規則は、PL が聞かずにタスクにして回す)で足りるので、agent-config の CLAUDE.md には足さない。

### テスト一覧

| テスト名 | 大きさ | 受け入れ条件 |
|---|---|---|
| 1. `test_install_ps1は_worktreeから走らせても_どの設定ディレクトリにも本体の作業ツリーの場所を書く` | 中 | 18 |
| 2. `test_install_ps1は_gitの外から走らせると_install_ps1のある場所を書く` | 中 | 19 |
| 3. `test_install_shは_worktreeから走らせても_どの設定ディレクトリにも本体の作業ツリーの場所を書く` | 中 | 20 |
| 4. `test_install_shは_gitの外から走らせると_install_shのある場所を書く` | 中 | 21 |

4つとも `tests/test_install_records_repo_path.medium.py` の中。中にしたのは、子プロセスを走らせ、ファイルに書くから。業務の規則の分かれ目は、git の中か外か(1・3 と 2・4)。設定ディレクトリが1つか2つかは、`.claude-work` があるときだけ足す今の動きなので、2つあるときに両方へ書くことを確かめれば足りる。

文書の行は、テストを作らず、次の確かめ方で確かめる(リポジトリのルートで流す)。

| 確かめ方 | 期待 | 受け入れ条件 |
|---|---|---|
| A | 1件 | 1 |
| B | 1 | 2 |
| C | 13件 | 2 |
| D | 1件 | 3 |
| E | 0 | 4 |
| F | 2件 | 5 |
| G | 2件 | 6 |
| H | 1件 | 7 |
| I | 1 | 8 |
| J | 1件 | 9 |
| K | 1件 | 10 |
| L | 1件 | 11 |
| M | 1 | 12 |
| N | 1件 | 13 |
| O | 1件 | 14 |
| P | 1件 | 15 |
| Q | 1件 | 16 |
| R | 2件 | 17 |
| S | 1件 | 24 |
| T | 1件 | 22 |
| U | 1件 | 23 |
| V | 1件 | 23 |
| W | 何も出ない | 25 |
| X | 全部通る(SKILL.md の箇条書きが60字以内も含む) | 25 |
| Y | 1〜4 が通る(その OS で動かない方は skipped) | 18〜21 |
| Z | 1件 | 26 |

```
A: grep -n "起こすまでのタスクは、ステータス「未着手」のチケットにしている。(ADR 0047-3)" claude/skills/task-team-lead/SKILL.md
B: grep -c "PL の会話でなくチケットにある(ADR 0047-3)" claude/skills/task-team-lead/SKILL.md
C: grep -n "ステータス「検討待ち」のチケットにしている\|ステータスの行とゴールの節だけで作っている\|ゴールの節には、タスクの文を書いている\|既定のブランチにコミットし、push している\|コミットせずに既定のブランチの作業ツリーに置いている\|番号の無いチケットを探している\|チェックアウトされているかを確かめている\|コミットせずに置き、利用者に伝えている\|SE への prompt にそのパスを添えている\|作業ツリーは、\`git worktree list\` の1行目\|番号を振った名前に変えて\|をチームのチケットにしている\|ステータスによらず進行中と読んでいる" claude/skills/task-team-lead/SKILL.md
D: grep -n "図の後に、名前とステータスを1行ずつ並べている" claude/skills/task-team-lead/SKILL.md
E: grep -c "バックログ" claude/skills/task-team-lead/SKILL.md
F: grep -n "チケットがあれば、それを直して使う。(ADR 0047-3)\|それを置き場へ移して使う。(ADR 0047-3)" claude/skills/task-team-se/SKILL.md
G: grep -n "作業用のブランチでしている(次の行のチケットは除く)\|チケットだけのリポジトリと、まだ始めていないチケット。(ADR 0047-3)" claude/CLAUDE.md
H: grep -n "AI の会話の状態によらず確かめられる" claude/skills/task-team-lead/CLAUDE.md
I: grep -c "親の目的・目指す状態に合うように動いている(ADR 0047-1)" claude/CLAUDE.md
J: grep -n "全体の規則が親の目的・目指す状態とぶつかったら、目的の方に従っている" claude/CLAUDE.md
K: grep -n "従ったら、どうずれていて、どう動いたかを利用者に伝えている" claude/CLAUDE.md
L: grep -n "リポジトリの手段を照らす目的と目指す状態は、そのリポジトリの中のものだけ" claude/CLAUDE.md
M: grep -c "agent-config のチケットになっている(ADR 0047-2)" claude/CLAUDE.md
N: grep -n "docs/tasks/<英語の短い名前>.md\` を1つ足している" claude/CLAUDE.md
O: grep -n "agent-config-path.txt\` に書いてある" claude/CLAUDE.md
P: grep -n "規則と目的のファイルと見出し、どうずれているか、どう動いたかを書いている" claude/CLAUDE.md
Q: grep -n "コミットせずに置き、agent-config の PL に任せている" claude/CLAUDE.md
R: grep -n "コードとデータは、チケットに写していない\|チケットの中身を返答で利用者に渡している" claude/CLAUDE.md
S: grep -n "agent-config-path.txt" README.md
T: grep -n "大のテストは無い" CLAUDE.md
U: grep -n "リポジトリの手段を照らすのは、その中の目的だけ" .claude/rules/global-claude-md.md
V: grep -n "agent-config に届く規則になっている" .claude/rules/global-claude-md.md
W: git diff -U0 main -- claude/ CLAUDE.md .claude/rules/global-claude-md.md | python -c "import sys;sys.path.insert(0,'claude/hooks');import check_rule_length as c;[print(l) for l in sys.stdin.buffer.read().decode('utf-8').splitlines() if l.startswith('+- ') and c.rule_length(l[3:].rstrip(chr(13)))>60]"
X: python -m unittest discover -s tests
Y: python tests/test_install_records_repo_path.medium.py -v
Z: grep -n "main の履歴と既定のブランチの作業ツリーにあるチケットの名前" claude/skills/task-team-lead/SKILL.md
```

O は `設定ディレクトリは、…` の行(受け入れ条件 14 の後半)も、P は「チケットは、ステータス「未着手」の行と、ゴールの節だけで書いている」の行(受け入れ条件 15 の前半)も、T は小と中のテストの行(受け入れ条件 22)も目で確かめる。

Windows では Y の 3・4 が skipped になるので、install.sh は PG が Git Bash で `t=$(mktemp -d) && mkdir "$t/.claude-work" && HOME="$t" bash -o igncr install.sh --yes && cat "$t/.claude/agent-config-path.txt" "$t/.claude-work/agent-config-path.txt"` を worktree のルートで流し(作業ツリーの install.sh は改行が CRLF なので `-o igncr` を付ける。今の install.sh がこの形で最後まで走ることは SE が確かめた)、2つとも本体の作業ツリーの場所(Git Bash の形 `C:/...`)が出ることを確かめ、実装の節に書く。

## 実装

## レビュー

### 設計レビュー(code-review low を設計の節に1回)

- 作業4: install は走らせた場所 `$repo` を書くので、worktree から走らせると、マージ後に `git worktree remove` で消える worktree の場所が残る。本体の作業ツリー(`git worktree list` の1行目)を書くようにする。(ADR 0047-2)
- 作業6: 「PL は…それを探し」に探す場所が無い。worktree で動く PL は自分の作業ツリーを探し、本体の作業ツリーに置かれた未コミットの drift-*.md を見つけない。`agent-config-path.txt` の場所を探す形にする(受け入れ条件 14 と確かめ方 L も)。(ADR 0047-2)
- テスト一覧・ADR の番号・仕様: 指摘なし。ADR 0047-1 は採用、0047-2 は提案のまま。

### 設計レビュー 2回目(code-review low を設計の節に1回)

- 1回目の指摘2件: 直っている(install は本体の作業ツリーを書き、PL は本体の作業ツリーを探す)。
- 作業3: small-chestnut 以外では、未コミットのチケットが SE の worktree に無く、チームが終わっても本体に「未着手」で残り、次のターンにまた見つかる。チームを起こすときの渡し方と、本体から消す時を決める。番号を振った後のチケットも毎ターン「見つけたチケット」になる。(ADR 0047-3)
- 作業3: `git worktree list` の1行目は本体の作業ツリーで、既定のブランチがチェックアウトされているとは限らない。そこでコミットし push すると別のブランチに入る。ブランチを確かめる行が要る。(ADR 0047-3)
- 作業3: `claude/CLAUDE.md` 原則1 に足す行が、12 行「作業は、既定のブランチではなく、作業用のブランチで(チケットだけのリポジトリは除く)」と逆を言う。12 行の除外を直す。全体の CLAUDE.md 原則1 に触れるので PL に知らせた。(ADR 0047-3)
- テスト一覧・ADR の番号・仕様: 指摘なし。ADR 0047-2 は採用、0047-3 は提案のまま。

### 設計レビュー 3回目(code-review low を設計の節に1回)

- 2回目の指摘3件: 直っている(SE が置き場へ移す・番号の無いチケットだけ探す・既定のブランチを確かめる・原則1 の除外)。
- 作業3: 番号は「main の履歴と進行中のチームの中で最大の次」(task-team-lead 32 行)のままなので、コミットせずに置いた番号付きのチケットが数に入らず、次のチケットに同じ番号が振られる。本体の作業ツリーの `docs/tasks/` にあるチケットも数に入れる。(ADR 0047-3)
- テスト一覧・ADR の番号・仕様・足す行の長さ: 指摘なし。ADR 0047-3 は提案のまま。

# 0103-no-trust-prompt-on-team-start

ステータス: 実装中
PC: Reo-Desktop

## 進捗

- 利用者待ち: なし
- [x] 1. やり方を決める(完了条件: 直し方を利用者が決め、要件の節に書いてある)
- [/] 2. Claude が新しいブランチの worktree を git で作ろうとすると止まる(依存: 1)(完了条件: テスト一覧のテストが通り、インストールした後のセッションで `git worktree add -b` を実行すると止まって、アプリに作らせるよう返る)
- [ ] 3. LogiFee でチームを作っても信頼を聞かれない(依存: 2)(完了条件: 利用者が LogiFee でチームを作り、信頼の問いが出なかったと返す)

## 難しさ

- SE: 高(原因をアプリの記録から調べ、直し方を決める)
- PG: 低(止める形と返す文は設計で決めてある)
- QA: 高(ADR を提案した設計のレビューで、フックで止める範囲がほかの使い方を壊さないかを判断する)

## ゴール

LogiFee の PL がチームを作るたびに、アプリの「このワークスペースを信頼しますか?」が出て、利用者が答えなければならない手間を無くす。

利用者の言葉(2026-11-27、PL の会話。LogiFee の worktree `3062-request-route` で出た信頼の問いの画面を添えて): 「logifee pl セッションで使っているのだが、SEが立つたびにこれが出るのが邪魔くさい」

範囲外: 信頼の確認を切る・緩めること(安全の設定)。

## 要件

### R1 新しいタスクの worktree はアプリに作らせる

- 要件: 新しいタスクの worktree は、PL が `git worktree add` で作らず、`start_session` の `use_worktree: true` でアプリに作らせる。
- なぜ: アプリは自分で作った worktree を信頼済みと記録するので、チームを作るたびに信頼の問いに答える手間が無くなる。
- 受け入れ条件 R1-1: LogiFee で次にチームを作ったとき、SE・PG・QA のどれでも信頼の問いが出ない。

### R2 git で新しいブランチの worktree を作るのをフックで止める

- 要件: Claude が `git worktree add` で新しいブランチの worktree を作ろうとしたら、フックで止め、アプリに作らせるよう返す。返す文で、アプリがほかのタスクのフォルダを使い回してもそのまま使うことと、ほかの PC から続けるタスクの作り方も伝える。skill には何も足さない。
- なぜ: アプリが作る流れをフックで固定すれば、PL がいちばん外れやすい道がふさがる。`git branch` の後の `git worktree add` のような抜け道はフックで見分けられないので、外れた原因(使い回されたフォルダを誤りと見たこと)への扱いを、止めたときに返す文で伝える。skill ではなく返す文に書けば、ほかのリポジトリで読まれる文章が増えない。利用者は「フックを作る」を選んだ(2026-11-27)。
- 受け入れ条件 R2-1: 新しいブランチを作る形の `git worktree add` は実行されず、アプリに作らせるよう返る。
- 受け入れ条件 R2-2: フォルダと既にあるブランチかコミットを渡す形(ほかの PC から続けるタスクの、skill `task-team-lead` の作り方)と、`--detach` の形の `git worktree add` は止まらない。
- 受け入れ条件 R2-3: 止めたときに返す文に、アプリがほかのタスクのフォルダを使い回してもそのまま使うことと、ほかの PC から続けるタスクは `git worktree add <フォルダ> <作業ブランチ>` で作ることが入っている。

### 分けたタスク

### 決まっていない問い

## 設計

### ADR

- 0103-1 新しいタスクの worktree はアプリに作らせ、git で新しいブランチの worktree を作るのをフックで止める(採用)

### 置くファイルと名前・データ

- `claude/hooks/git_command_args.py`(新しく作る): Bash・PowerShell のコマンドを読む部分を、2つのフックで使えるようにまとめる。(R2)
  - `SEPARATORS`: `block_history_erasing_push.py` から移す。
  - `git_args(segment: str) -> list[str] | None`: 1つのコマンドが git なら、大域オプション(`-C`・`-c` は値も)を飛ばした、サブコマンドから後ろのトークン。そうでなければ None。`block_history_erasing_push.py` の `push_args` の前半を移したもの。
- `claude/hooks/block_history_erasing_push.py`(直す): `SEPARATORS` と `git_args` を `git_command_args` から読む。動きは変えない。
- `claude/hooks/block_new_branch_worktree.py`(新しく作る): PreToolUse フック。(R2・ADR 0103-1)
  - docstring に「ADR 0103-1」を書く。
  - 止める形(R2-1): `git_args` が `worktree add` で始まり、その後ろに、`-b`・`-B`(`-bname` のように続けて書いたものも)があるか、`--detach`・`-d` が無くて位置引数(`-` で始まらないトークン。`--reason` の次のトークンは値なので数えない)が1つだけのもの。
  - 通す形(R2-2): 位置引数が2つで `-b`・`-B` が無いもの、`--detach`・`-d` があるもの、`worktree add` 以外のすべて。
  - &&・||・;・|・改行でつないだコマンドは、1つずつ見て、1つでも止める形があれば止める。
  - 止めるときは、stderr に次の文を書いて exit 2。(R2-1・R2-3)「新しいブランチの worktree を git で作るのを止めました。新しいタスクの worktree は、start_session の use_worktree: true でアプリに作らせ、アプリがほかのタスクのフォルダを使い回しても、そのまま使ってください。アプリが作った worktree は信頼済みと記録され、開くときに信頼を聞かれません。ほかの PC から続けるタスクは、git fetch の後に git worktree add <フォルダ> <作業ブランチ> で作ってください。」
  - 入力の JSON が読めないときと、`tool_input.command` が無いときは、何も返さずに通す(`block_history_erasing_push.py` と同じ)。
- `claude/user-settings.json`(直す): `hooks.PreToolUse` の matcher `Bash|PowerShell` の `hooks` に、`block_history_erasing_push.py` の次に1つ足す。command は、ほかと同じ形の `P=python3; python3 -c '' 2>/dev/null || P=python; "$P" "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/block_new_branch_worktree.py"`。(R2)
- `docs/specs/block_new_branch_worktree.py.md`(設計のコミットで作った): フックの外から見える動き。実装がこれと合うようにする。(R2)

### 手順

1. `git_command_args.py` を作り、`block_history_erasing_push.py` をそれを使う形に直して、`python -m unittest tests/test_block_history_erasing_push.py` が通ることを確かめ、このコミットだけで分ける(動きを変えないコミット)。(R2)
2. テスト一覧のテストを先に書き、通らないことを確かめる。(R2-1・R2-2)
3. `block_new_branch_worktree.py` を書き、`user-settings.json` に足す。(R2)
4. `python -m unittest discover -s tests -p "*test_*.py"` が全部通ることを確かめる。(R2)
5. PL が main にマージしてインストールした後、新しいセッションで `git worktree add -b` を実行すると止まり、上の文が返ることを確かめる(進捗 2 の完了条件)。(R2-1)
6. 利用者が LogiFee で次にチームを作り、信頼を聞かれないかを確かめる(下の「利用者がする操作」)。(R1-1)

### 利用者がする操作

- 何を: インストールした後に、LogiFee の PL セッションで、いつものようにチームを作ってもらう。
- ゴールにどうつながるか: 信頼の問いが出なくなったことを、実際の画面で確かめる(R1-1)。
- なぜ利用者の手でか: 信頼の問いは利用者の画面にだけ出て、Claude からは出たかどうかが見えない。
- 手順: LogiFee の PL セッションに、次のタスクのチームを作るよう頼む。LogiFee の PL が `git worktree add -b` で作ろうとすればフックで止まり、アプリに作らせるほうへ戻る。
- 終わったら返すこと: SE・PG・QA のどれかで信頼の問いが出たか、出なかったか。
- 元に戻せるか: 戻せる(チームを作るだけ)。

### テスト一覧

| テスト名 | テストサイズ | 受け入れ条件 |
|---|---|---|
| test_block_new_branch_worktree.py: 新しいブランチを作るworktree_addは止めてアプリに作らせるよう返す(`-b`・`-B`・`-bname`・フォルダだけ・`git -C <フォルダ> worktree add -b`・&& でつないだもの) | small | R2-1 |
| test_block_new_branch_worktree.py: 止めたときに返す文は使い回されたフォルダをそのまま使うこととほかのPCの作り方を伝える(`git worktree add -b <ブランチ> <フォルダ> origin/<ブランチ>` で止めたときも) | small | R2-3 |
| test_block_new_branch_worktree.py: 既にあるブランチかdetachのworktree_addは通す(フォルダとブランチ・`--detach`・`-d`・`--reason` の値を数えないこと) | small | R2-2 |
| test_block_new_branch_worktree.py: worktree_add以外のコマンドは通す(`git worktree list`・`git push`・`echo`) | small | R2-2 |

- `test_block_history_erasing_push.py` は残す(手順1で動きを変えないことを確かめる)。

### サブタスクの前提

### 設計への問い

- 止める形の行(R2-1)のとおりに作ると、フォルダだけの形にリダイレクトを付けた `git worktree add ../wt 2>&1`(`2>&1 | Out-String`・`> log.txt` も)は通る。`2>&1` や `>`・`log.txt` が `-` で始まらず、位置引数に数えられるため(実装したフックの判定で確かめた)。このコマンドは新しいブランチを作るので、R2-1「新しいブランチを作る形の `git worktree add` は実行されず」と食い違う。`-b`・`-B` を含む形は、リダイレクトがあっても止まる。PG の案: リダイレクト(`>`・`2>`・`2>&1` と、`>` の次の出力先)は位置引数に数えず、R2-1 のテストにこの形を足し、仕様にも1行足す。別の案は、今の設計のままにして、通ることを ADR の抜け道に認める。どちらにするかを決めてほしい。
  - 今の実装は、今の設計の行のとおり。

## 実装

## レビュー

- 設計: 止める形が `-b` を含む `git worktree add` を全部止めるので、ほかの PC から続けるタスクの `git worktree add -b <ブランチ> <フォルダ> origin/<ブランチ>` も止まり、task-team-lead の「use_worktree: false で開始する」手順と食い違う「use_worktree: true でアプリに作らせる」が返る。R2-2 と ADR 0103-1 の理由3は、2つの位置引数で書いたときだけ成り立つ。返す文にほかの PC の作り方を足すか、通す形を広げるかを決め、テスト一覧に足す。
  - 直した所(SE): 返す文に、ほかの PC から続けるタスクは `git fetch` の後に `git worktree add <フォルダ> <作業ブランチ>` で作ることを足した(R2-3)。通す形は広げない(止める形を簡単に保つ)。R2-2 に skill の作り方だと書き、ADR の理由3を直し、テスト一覧に R2-3 のテストを足した。
- 設計: R2 のなぜと ADR 0103-1 の理由2は、フックで PL が外れる先が無くなるとするが、`git branch <名前>` の後の `git worktree add <フォルダ> <名前>` は通る。PL が外れた原因(アプリが使い回したフォルダを誤りと見たこと)には設計のどこも触れていないので、止められた PL がこの形に回れば信頼の問いが残る(R1-1)。返す文に、使い回されたフォルダでもそのまま使うことを足すか、ADR の理由をこの抜け道を認めた文に直す。
  - 直した所(SE): 両方した。返す文に、アプリがほかのタスクのフォルダを使い回してもそのまま使うことを足し(R2-3)、R2 のなぜと ADR の理由2を、抜け道を認め、外れた原因への扱いを返す文で伝える文に直した。ADR の捨てた案に、抜け道も止める案を足した。
- 直しの確かめ(QA): 2件とも直った。ADR 0103-1 を採用にした。

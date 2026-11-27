# 0103-1 新しいタスクの worktree はアプリに作らせ、git で新しいブランチの worktree を作るのをフックで止める

状態: 採用
日付: 2026-11-27
対象: block_new_branch_worktree.py

## 決めたこと

Claude が `git worktree add` で新しいブランチの worktree を作るのを PreToolUse フックで止め、新しいタスクの worktree は `start_session` の `use_worktree: true` でアプリに作らせるよう返す。

## 捨てた案

1. skill `task-team-lead` に、アプリがほかのタスクのフォルダを使い回しても、そのまま使うと書く: 同じことを、PL が外れようとしたときにフックが返す文で伝えられる。skill に書くと、ほかのリポジトリで読まれる文章が増える。
2. `start_session` の前に、SE を `use_worktree: true` で開始しているかを確かめるか、`true` に書き換えるフック: 正しく `false` で開始する、ほかの PC から続けるタスクと、チケットだけのリポジトリを、フックから見分けられない。書き換えると、この2つが壊れる。
3. `git branch` の後の `git worktree add <フォルダ> <ブランチ>` や、`--detach` の後の `git switch -c` のような抜け道も止める: ほかの PC から続けるタスクなどの正しい使い方と、フックから見分けられない。
4. 信頼の確認を切るか緩める: 安全の設定に触る。

## 理由

1. アプリは、自分で作った worktree を、作ったときに信頼済みと記録する(`%APPDATA%\Claude\git-worktrees.json` の `autoTrusted: true`)。PL が `git worktree add` で作った worktree は記録されず、そこを `cwd` にして最初に開始するセッションで、利用者が信頼を聞かれる。
2. LogiFee の PL は、アプリが SE の worktree に、片付ける前のほかのタスクのフォルダを使い回したのを誤りと見て、2026-11-15 から `git worktree add -b` で worktree を自分で作り、チームを作るたびに利用者が信頼を聞かれていた。フックは、この道をふさぎ、止めたときに、使い回されたフォルダもそのまま使うよう返して、外れた原因に応える。抜け道(捨てた案3)は残るが、止められた PL は返す文を読んでから次の手を選ぶ。
3. 止めたときに返す文で、ほかの PC から続けるタスクは skill `task-team-lead` の `git worktree add <フォルダ> <作業ブランチ>` で作るよう伝え、この形と `--detach` は止めないので、今の手順の例外は動く。

# 0103-1 新しいタスクの worktree はアプリに作らせ、git で新しいブランチの worktree を作るのをフックで止める

状態: 提案
日付: 2026-11-27
対象: block_new_branch_worktree.py

## 決めたこと

Claude が `git worktree add` で新しいブランチの worktree を作るのを PreToolUse フックで止め、新しいタスクの worktree は `start_session` の `use_worktree: true` でアプリに作らせる。

## 捨てた案

1. skill `task-team-lead` に、アプリがほかのタスクのフォルダを使い回しても、そのまま使うと書く: アプリが作る流れをフックで固定すれば、PL が外れる先が無くなるので、使い回しの扱いは要らない。他のリポジトリで読まれる文章も増える。
2. `start_session` の前に、SE を `use_worktree: true` で開始しているかを確かめるか、`true` に書き換えるフック: 正しく `false` で開始する、ほかの PC から続けるタスクと、チケットだけのリポジトリを、フックから見分けられない。書き換えると、この2つが壊れる。
3. 信頼の確認を切るか緩める: 安全の設定に触る。

## 理由

1. アプリは、自分で作った worktree を、作ったときに信頼済みと記録する(`%APPDATA%\Claude\git-worktrees.json` の `autoTrusted: true`)。PL が `git worktree add` で作った worktree は記録されず、そこを `cwd` にして最初に開始するセッションで、利用者が信頼を聞かれる。
2. LogiFee の PL は、アプリが SE の worktree に、片付ける前のほかのタスクのフォルダを使い回したのを誤りと見て、2026-11-15 から worktree を自分で作り、チームを作るたびに利用者が信頼を聞かれていた。規則の文では、同じことがまた起きたときに外れるのを防げない。
3. 新しいブランチを作らない `git worktree add <フォルダ> <既にあるブランチ>`(ほかの PC から続けるタスク)と `--detach` は止めないので、今の手順の例外はそのまま動く。

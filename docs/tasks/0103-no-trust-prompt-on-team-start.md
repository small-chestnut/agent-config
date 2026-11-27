# 0103-no-trust-prompt-on-team-start

ステータス: 壁打ち中
PC: Reo-Desktop

## 進捗

- 利用者待ち: skill に足す行の案を見て、設計に進めるかを決めてもらう([0103-no-trust-prompt-on-team-start SE](#local_da3e5b00-914c-4151-b69e-b9f25b16d46b))
- [/] 1. やり方を決める(完了条件: 直し方を利用者が決め、要件の節に書いてある)

## 難しさ

- SE: 中(原因はアプリの動きの調べで分かり、変える文は少ない見込み)

## ゴール

LogiFee の PL がチームを作るたびに、アプリの「このワークスペースを信頼しますか?」が出て、利用者が答えなければならない手間を無くす。

利用者の言葉(2026-11-27、PL の会話。LogiFee の worktree `3062-request-route` で出た信頼の問いの画面を添えて): 「logifee pl セッションで使っているのだが、SEが立つたびにこれが出るのが邪魔くさい」

範囲外: 信頼の確認を切る・緩めること(安全の設定)。

## 要件

### R1 SE の worktree はアプリに作らせる

- 要件: LogiFee の PL は、skill `task-team-lead` の今の手順のとおり、SE を `use_worktree: true` で開始し、worktree をアプリに作らせる。`git worktree add` で自分で作るのをやめる。
- なぜ: アプリは自分で作った worktree を信頼済みと記録するので、チームを作るたびに信頼の問いに答える手間が無くなる。
- 受け入れ条件 R1-1: LogiFee で次にチームを作ったとき、SE・PG・QA のどれでも信頼の問いが出ない。

### R2 アプリが使い回したフォルダをそのまま使う

- 要件: アプリが SE の worktree に、ほかのタスクのフォルダを使い回しても、PL がそのまま使うことを、skill `task-team-lead` に書く。R1 は LogiFee の PL にも伝える。
- なぜ: LogiFee の PL は、使い回されたフォルダを誤りと見て、worktree を自分で作るようになった。skill に書かなければ、同じことがまた起きたときに、また自分で作り出す。
- 受け入れ条件 R2-1: skill `task-team-lead` を読んだ PL が、SE の worktree のフォルダの名前がほかのタスクのものでも、開始し直さず、そのフォルダで QA と PG を開始する。

### 分けたタスク

### 決まっていない問い

- 調べて分かった事実は次のとおり。
  - アプリは、`start_session` の `use_worktree: true` で自分が作った worktree を、作ったときに信頼済みと記録する(`%APPDATA%\Claude\git-worktrees.json` の `autoTrusted: true`)。
  - LogiFee の PL は、2026-11-15 の 2921 から、skill `task-team-lead` の「SE は `use_worktree: true`」に従わず、`git worktree add` で worktree を自分で作り、3つとも `use_worktree: false` で開始している。この worktree はアプリの記録に無く、SE が最初に開くときに信頼を聞かれる。
  - 切り替えたきっかけ: 2921 の SE を `use_worktree: true` で開始したら、アプリが、12:48 にアーカイブした 2920 のチームの worktree(片付ける前のもの)のフォルダを使い回し、そこに 2921 のブランチ(develop の先端から)を作った。PL はこれを誤りと見て開始し直し、以後ずっと自分で作っている。

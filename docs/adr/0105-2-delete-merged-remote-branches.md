# 0105-2 既定のブランチにマージした作業ブランチは、マージの後にリモートからも消す

状態: 提案
日付: 2026-11-28
対象: task-team-lead

## 決めたこと

PL は、作業ブランチを既定のブランチにマージして push した後、手元の作業ブランチに加えて、リモートの作業ブランチも消す(詳しい文は skill `task-team-lead`)。

## 捨てた案

1. 今どおり、リモートの作業ブランチを残す: 残していたのは、利用者が前にいた現場の慣習で、決まりには残す理由が無い。作業ブランチを push するのは、ほかの PC から続けるため(ADR 0056-5)で、マージの後には要らない。残すと、リモートのブランチがタスクの数だけ増える(2026-11-28 に、origin の 100 本のうち 99 本がマージ済みだった)。
2. GitHub の、マージしたら head のブランチを自動で消す設定を使う: この設定は、GitHub の画面でプルリクエストをマージしたときに効く。このリポジトリは手元でマージして push するので、効かない(https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-the-automatic-deletion-of-branches 。2026-11-28 に調べた)。
3. 全体の CLAUDE.md の、マージして push する行に、リモートのブランチを消すことも書く: リモートに作業ブランチを上げるのは、チケットのコミットを push するフック(task-team のタスク)で、マージするのも PL なので、skill `task-team-lead` に置けば足りる。全体の CLAUDE.md は、どのリポジトリでも読まれる。

## 理由

1. 利用者は、どこまでのブランチを残すかを、前の現場の慣習でなく、広く使われるやり方に沿わせたい(2026-11-28)。
2. GitHub flow は、プルリクエストをマージしたらブランチを消すとしている。消しても、コミットの履歴は残る(https://docs.github.com/en/get-started/using-github/github-flow 。2026-11-28 に調べた)。
3. マージした作業ブランチのコミットは、既定のブランチの履歴に残るので、ブランチを消しても元に戻せる(全体の CLAUDE.md の安全の原則の目的)。

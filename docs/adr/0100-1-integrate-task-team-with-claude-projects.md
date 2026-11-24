# 0100-1 task-team を「プロジェクト」機能に統合する試しを、実際のタスクで続ける

状態: 提案
日付: 2026-11-25
対象: 全体

## 決めたこと

task-team の手順と規則を Claude の「プロジェクト」機能に肩代わりさせて減らす統合を、agent-config の決まりを環境のセットアップスクリプトで届ける形で、実際の小さいタスクで試しながら続ける。

## 捨てた案

1. 統合をやめ、今の task-team のまま進める: 決まりが届かなければ安全の決まりの守りが弱くなるのでやめる、と PL は利用者に伝えていたが、試験で届いた(理由2)。
2. リポジトリの `.claude/settings.json` にフックと permissions を置いて届ける: プロジェクトのスレッドでは、リポジトリのフックと permissions は効かない(https://code.claude.com/docs/en/claude-projects の What threads pick up from your repositories)。

## 理由

1. 利用者が統合で一番得たいのは、task-team に書いてある手順と規則を、Anthropic の「プロジェクト」機能にカバーさせて減らすこと。
2. 2026-11-25 に、リポジトリの無いプロジェクトのクラウドのスレッド1本で試した。環境のセットアップスクリプトで agent-config をインストールすると、全体の CLAUDE.md が読まれ、skill を呼べ、`PreToolUse` と `PostToolUse` のフックが動き、deny が `rm -r` を拒否した。セットアップスクリプトは `git show 3a1ac89:docs/tasks/0100-try-claude-projects/setup-script.sh`、スレッドの出力は `git show 875b072:docs/tasks/0100-try-claude-projects/result.md`。
3. `~/.claude/` に置いたフックと deny がクラウドで効くことは、公式文書に書かれていない(2026-11-25 に読んだ https://code.claude.com/docs/en/settings の Settings in cloud sessions は、利用者の PC の `~/.claude/settings.json` を読まないとだけ書く)。
4. SE の見積もりでは、task-team の規則 258 行のうち 72 行(28%)を肩代わりする見込み(`git show cc54948:docs/tasks/0100-try-claude-projects/covered-rules.md`)。前提は、タスク1つをスレッド1本で進め、SE・PG・QA のやりとりをサブエージェントに変えること。この前提は ADR 0057-2 の捨てた案3の理由と ADR 0007-1 の理由1と逆向きで、撤回するかを利用者にまだ聞いていない。試験では、文で質問して待つスレッドが Overview の「Waiting on you」に出ず「アイドル」に出て、質問はプロジェクトの会話に出た。このため、72 行のうち利用者待ちと、かんばんの待ちの表示の行が肩代わりされるかは、まだ決まらない。
5. 試していないのは、リポジトリを付けたプロジェクト・複数のスレッド・QA の独立・マージ・この PC が要る仕事。公式文書には、スレッドどうしのやりとり・独立したレビュー・マージの担当が書かれていない(https://code.claude.com/docs/en/claude-projects )。

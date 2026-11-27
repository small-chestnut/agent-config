# block_new_branch_worktree.py

## ADR

- 0103-1 新しいタスクの worktree はアプリに作らせ、git で新しいブランチの worktree を作るのをフックで止める

## 動き

- Bash・PowerShell の `git worktree add` が、`-b`・`-B`(`-bname` のように続けて書いたものも)を含むか、`--detach`・`-d` が無くてフォルダだけを渡していれば、止めて、新しいタスクの worktree は `start_session` の `use_worktree: true` でアプリに作らせるよう返す。
- 止めたときに返す文は、アプリがほかのタスクのフォルダを使い回しても、そのまま使うことと、ほかの PC から続けるタスクは `git fetch` の後に `git worktree add <フォルダ> <作業ブランチ>` で作ることも伝える。
- フォルダと既にあるブランチかコミットを渡す `git worktree add` と、`--detach`・`-d` を含む `git worktree add` は通す。
- `--reason` の次のトークンは値として読み、フォルダやブランチに数えない。
- リダイレクト(`>`・`>>`・`2>`・`2>&1`・`*>`・`&>`・`>log.txt` など)と、離れて書いた出力先は、フォルダやブランチに数えない。
- &&・||・;・|・改行でつないだコマンドは、1つずつ見て、1つでも止める形があれば止める。
- `git worktree add` 以外のコマンドは、何も返さずに通す。

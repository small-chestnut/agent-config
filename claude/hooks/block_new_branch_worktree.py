"""新しいブランチの worktree を作る git worktree add を、走らせる前に止める(Claude Code の PreToolUse フック)。

新しいタスクの worktree はアプリに作らせる(ADR 0103-1)。
Bash・PowerShell のコマンドを &&・||・;・|・改行で区切り、git worktree add の引数を見る。
止めるのは、-b・-B を含むものと、--detach・-d が無くてフォルダだけを渡すもの。
止めたら stderr にアプリに作らせるよう書いて exit 2(コマンドは走らない)。
"""
import json
import re
import sys

from git_command_args import SEPARATORS, git_args

REDIRECT = re.compile(r"^[0-9*&]?(>>?|<)")
MESSAGE = ("新しいブランチの worktree を git で作るのを止めました。"
           "新しいタスクの worktree は、start_session の use_worktree: true でアプリに作らせ、"
           "アプリがほかのタスクのフォルダを使い回しても、そのまま使ってください。"
           "アプリが作った worktree は信頼済みと記録され、開くときに信頼を聞かれません。"
           "ほかの PC から続けるタスクは、git fetch の後に "
           "git worktree add <フォルダ> <作業ブランチ> で作ってください。")


def makes_new_branch(args: list[str]) -> bool:
    """git worktree add の add の後ろの引数が、新しいブランチを作る形か。"""
    detached = False
    positionals = 0
    rest = iter(args)
    for a in rest:
        if a.startswith(("-b", "-B")):
            return True
        if a in ("--detach", "-d"):
            detached = True
        elif a == "--reason":
            next(rest, None)
        elif redirect := REDIRECT.match(a):
            if redirect.end() == len(a):  # 出力先が離れている
                next(rest, None)
        elif not a.startswith("-"):
            positionals += 1
    return not detached and positionals == 1


def should_block(command: str) -> bool:
    for segment in SEPARATORS.split(command):
        args = git_args(segment.strip())
        if args and args[:2] == ["worktree", "add"] and makes_new_branch(args[2:]):
            return True
    return False


def main() -> int:
    try:
        event = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return 0
    command = (event.get("tool_input") or {}).get("command")
    if not command or not should_block(command):
        return 0
    sys.stderr.reconfigure(encoding="utf-8")
    print(MESSAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

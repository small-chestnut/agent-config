"""リモートの履歴を消す git push を、走らせる前に止める(Claude Code の PreToolUse フック)。

Bash・PowerShell のコマンドを &&・||・;・|・改行で区切り、git push の引数を見る。
止めるのは、--force・--delete・--mirror・--prune、f か d を含む短いフラグ(-fu など)、
+ か : で始まる指定(+main・:main)。止めたら stderr に理由を書いて exit 2(コマンドは走らない)。
--force-with-lease は、どの位置にあっても利用者の確認に回す(permissionDecision: ask)。
"""
import json
import re
import shlex
import sys
from pathlib import Path

SEPARATORS = re.compile(r"&&|\|\||[;|\n]")
ERASING_LONG_FLAGS = ("--force", "--delete", "--mirror", "--prune")
LEASE = "--force-with-lease"


def push_args(segment: str) -> list[str] | None:
    """1つのコマンドが git push なら、push の後ろの引数。そうでなければ None。"""
    try:
        tokens = shlex.split(segment)
    except ValueError:
        tokens = segment.split()
    if not tokens or Path(tokens[0]).name not in ("git", "git.exe"):
        return None
    i = 1
    while i < len(tokens) and tokens[i].startswith("-"):
        i += 2 if tokens[i] in ("-C", "-c") else 1
    if i >= len(tokens) or tokens[i] != "push":
        return None
    return tokens[i + 1:]


def erasing_arg(args: list[str]) -> str | None:
    """push の引数のうち、リモートの履歴を消すもの。"""
    for a in args:
        if a.startswith("--"):
            if a.split("=")[0] in ERASING_LONG_FLAGS:
                return a
        elif a.startswith("-"):
            if "f" in a or "d" in a:
                return a
        elif a.startswith(("+", ":")):
            return a
    return None


def judge(command: str) -> tuple[str, str] | None:
    """("deny" か "ask", 当たった引数)。ふつうの push と push 以外は None。"""
    asked = None
    for segment in SEPARATORS.split(command):
        args = push_args(segment.strip())
        if args is None:
            continue
        erasing = erasing_arg(args)
        if erasing:
            return "deny", erasing
        lease = next((a for a in args if a.startswith(LEASE)), None)
        if lease and asked is None:
            asked = "ask", lease
    return asked


def main() -> int:
    try:
        event = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return 0
    command = (event.get("tool_input") or {}).get("command")
    if not command:
        return 0
    found = judge(command)
    if found is None:
        return 0
    decision, arg = found
    if decision == "deny":
        sys.stderr.reconfigure(encoding="utf-8")
        print(f"リモートの履歴を消す push なので止めました({arg})。"
              f"履歴の書き換えを頼まれたときは {LEASE} を使ってください。", file=sys.stderr)
        return 2
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": f"リモートの履歴を書き換える push です({arg})。",
    }}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

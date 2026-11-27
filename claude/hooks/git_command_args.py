"""Bash・PowerShell のコマンドから git の引数を読む(PreToolUse フックが使う)。"""
import re
import shlex
from pathlib import Path

SEPARATORS = re.compile(r"&&|\|\||[;|\n]")


def git_args(segment: str) -> list[str] | None:
    """1つのコマンドが git なら、大域オプションを飛ばした、サブコマンドから後ろ。そうでなければ None。"""
    try:
        tokens = shlex.split(segment)
    except ValueError:
        tokens = segment.split()
    if not tokens or Path(tokens[0]).name not in ("git", "git.exe"):
        return None
    i = 1
    while i < len(tokens) and tokens[i].startswith("-"):
        i += 2 if tokens[i] in ("-C", "-c") else 1
    return tokens[i:]

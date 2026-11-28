"""Bash・PowerShell のコマンドから git の引数を読む(PreToolUse フックが使う)。"""
import re
import shlex
from pathlib import Path

SEPARATORS = re.compile(r"&&|\|\||[;|\n]")


def tokens_of(segment: str) -> list[str]:
    """1つのコマンドを、空白と引用符で語に分ける。"""
    try:
        return shlex.split(segment)
    except ValueError:
        return segment.split()


def _git_tokens(segment: str) -> tuple[list[str], int] | None:
    """1つのコマンドが git なら、(語, サブコマンドの位置)。そうでなければ None。"""
    tokens = tokens_of(segment)
    if not tokens or Path(tokens[0]).name not in ("git", "git.exe"):
        return None
    i = 1
    while i < len(tokens) and tokens[i].startswith("-"):
        i += 2 if tokens[i] in ("-C", "-c") else 1
    return tokens, i


def git_args(segment: str) -> list[str] | None:
    """1つのコマンドが git なら、大域オプションを飛ばした、サブコマンドから後ろ。そうでなければ None。"""
    found = _git_tokens(segment)
    return None if found is None else found[0][found[1]:]


def git_folder(segment: str, cwd: str) -> str:
    """git が走るフォルダ。大域オプションの -C を cwd から順にたどる。"""
    found = _git_tokens(segment)
    folder = Path(cwd)
    if found is None:
        return str(folder)
    tokens, end = found
    i = 1
    while i < end:
        if tokens[i] in ("-C", "-c"):
            if tokens[i] == "-C" and i + 1 < len(tokens):
                folder = folder / tokens[i + 1]
            i += 2
        else:
            i += 1
    return str(folder)

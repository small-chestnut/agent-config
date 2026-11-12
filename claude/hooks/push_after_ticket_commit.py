"""チケットの md をコミットした直後に、その作業ブランチを push する(Claude Code の PostToolUse フック。ADR 0071-1・0056-5)。

Bash・PowerShell で `git commit` を走らせた後に動く。HEAD を見る作業ツリーは、`git -C <パス> commit` なら <パス>、
無ければ `git commit` より前の最後の `cd <パス>`・`Set-Location <パス>`、どちらも無ければ入力の cwd。
チケットは、HEAD のコミットで足した・直した・消した .md のうち、HEAD かその親での冒頭5行に「ステータス: 」で始まる行があるもの。
チケットが無い・リモートが無い・HEAD がブランチに居ないときは何もしない。
リモートは origin、無ければ `git remote` の1行目。上流があれば `git push`、無ければ `git push -u <リモート> HEAD`。
結果は additionalContext で Claude に知らせ、exit 0 で終わる。
"""
import json
import os
import re
import subprocess
import sys

STATUS_PREFIX = "ステータス: "
HEAD_LINES = 5

QUOTED_OR_BARE = r"""(?:"[^"]*"|'[^']*'|[^\s;&|]+)"""
COMMIT = re.compile(r"\bgit\s+(?:-C\s+(?P<path>" + QUOTED_OR_BARE + r")\s+)?commit\b")
CHANGE_DIR = re.compile(r"(?:\bcd|\bSet-Location)\s+(?P<path>" + QUOTED_OR_BARE + ")")


def run_git(args: list[str], cwd: str) -> tuple[int, str]:
    """git を cwd で動かし、(終了コード, 標準出力と標準エラーを合わせた文) を返す。"""
    try:
        done = subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                              encoding="utf-8", errors="replace")
    except OSError as e:
        return 1, str(e)
    return done.returncode, (done.stdout + done.stderr).strip()


def unquote(path: str) -> str:
    if len(path) >= 2 and path[0] == path[-1] and path[0] in "\"'":
        return path[1:-1]
    return path


def work_tree(command: str, cwd: str) -> str | None:
    """HEAD を見る作業ツリー。`git commit` を含まないコマンドは None。"""
    commit = COMMIT.search(command)
    if not commit:
        return None
    path = commit.group("path")
    if path is None:
        moves = list(CHANGE_DIR.finditer(command[:commit.start()]))
        path = moves[-1].group("path") if moves else None
    if path is None:
        return cwd
    return os.path.join(cwd, unquote(path))  # 絶対パスなら、join は絶対パスの方を返す


def has_status_line(text: str) -> bool:
    return any(line.startswith(STATUS_PREFIX) for line in text.splitlines()[:HEAD_LINES])


def touches_ticket(tree: str, git) -> bool:
    code, out = git(["diff-tree", "-r", "--root", "--no-commit-id", "--name-status", "--no-renames", "HEAD"], tree)
    if code != 0:
        return False
    for line in out.splitlines():
        status, _, path = line.partition("\t")
        if not path.endswith(".md"):
            continue
        for rev in ("HEAD", "HEAD~1"):
            code, text = git(["show", f"{rev}:{path}"], tree)
            if code == 0 and has_status_line(text):
                return True
    return False


def pick_remote(tree: str, git) -> str | None:
    code, out = git(["remote"], tree)
    remotes = out.splitlines() if code == 0 else []
    if not remotes:
        return None
    return "origin" if "origin" in remotes else remotes[0]


def push_message(event: dict, git=run_git) -> str | None:
    """知らせる文。何もしないときは None。"""
    if event.get("tool_name") not in ("Bash", "PowerShell"):
        return None
    command = (event.get("tool_input") or {}).get("command") or ""
    tree = work_tree(command, event.get("cwd") or os.getcwd())
    if tree is None:
        return None
    code, branch = git(["symbolic-ref", "--short", "-q", "HEAD"], tree)
    if code != 0 or not branch:
        return None
    if not touches_ticket(tree, git):
        return None
    remote = pick_remote(tree, git)
    if remote is None:
        return None
    code, _ = git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], tree)
    push_args = ["push"] if code == 0 else ["push", "-u", remote, "HEAD"]
    code, out = git(push_args, tree)
    if code == 0:
        return f"チケットのコミットを {remote}/{branch} へ push した。"
    return f"チケットのコミットの push に失敗した:\n{out}"


def main() -> int:
    try:
        event = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return 0
    message = push_message(event)
    if message is None:
        return 0
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                             "additionalContext": message}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

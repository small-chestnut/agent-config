"""リモートの履歴を消す git push を、走らせる前に止める(Claude Code の PreToolUse フック)。

Bash・PowerShell のコマンドを &&・||・;・|・改行で区切り、git push の引数を見る。
止めるのは、--force・--mirror・--prune、-d のほかの f か d を含む短いフラグ(-fu など)、
+ で始まる refspec(+main)。止めたら stderr に理由を書いて exit 2(コマンドは走らない)。
リモートのブランチを消す push(--delete・-d・:<ブランチ>)は、消すブランチのリモートの今の先端が
みな、手元のリモートの既定のブランチの履歴に含まれるときだけ通す。確かめられなければ止める。
--force-with-lease は、どの位置にあっても利用者の確認に回す(permissionDecision: ask)。
"""
import json
import os
import subprocess
import sys
import time

from git_command_args import SEPARATORS, git_args, git_folder, git_options, tokens_of

ERASING_LONG_FLAGS = ("--force", "--mirror", "--prune")
DELETE_FLAGS = ("--delete", "-d")
VALUE_FLAGS = ("-o", "--push-option", "--receive-pack", "--exec", "--repo")
FOLDER_COMMANDS = ("cd", "chdir", "set-location", "sl", "pushd", "push-location", "popd",
                   "pop-location")
REPO_OPTIONS = ("--git-dir", "--work-tree")
LEASE = "--force-with-lease"
TIME_LIMIT = 20
HEADS = "refs/heads/"


class GitFailed(Exception):
    """git が失敗したか、時間を使い切った。"""


class Git:
    """フック全体の時間の上限の中で、git を走らせて答えを読む。"""

    def __init__(self, deadline: float):
        self.deadline = deadline

    def _run(self, repo: str, *args: str) -> subprocess.CompletedProcess:
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise GitFailed("時間切れ")
        try:
            return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=remaining)
        except subprocess.TimeoutExpired:
            raise GitFailed("時間切れ")
        except OSError as e:
            raise GitFailed(f"git を走らせられない: {e}")

    def ls_remote(self, repo: str, remote: str) -> dict[str, str]:
        """リモートの今のブランチの名前と先端のコミット。"""
        result = self._run(repo, "ls-remote", "--heads", remote)
        if result.returncode != 0:
            raise GitFailed(f"git ls-remote が失敗した: {result.stderr.strip()}")
        heads = {}
        for line in result.stdout.splitlines():
            sha, _, ref = line.partition("\t")
            if ref.startswith(HEADS):
                heads[ref[len(HEADS):]] = sha
        return heads

    def default_branch(self, repo: str, remote: str) -> str:
        """refs/remotes/<リモート>/HEAD が指す ref。"""
        result = self._run(repo, "symbolic-ref", "-q", f"refs/remotes/{remote}/HEAD")
        if result.returncode != 0 or not result.stdout.strip():
            raise GitFailed(f"refs/remotes/{remote}/HEAD が無い")
        return result.stdout.strip()

    def is_ancestor(self, repo: str, sha: str, ref: str) -> bool:
        """sha が ref の履歴に含まれるか。"""
        result = self._run(repo, "merge-base", "--is-ancestor", sha, ref)
        if result.returncode in (0, 1):
            return result.returncode == 0
        raise GitFailed(f"先端のコミット {sha[:12]} が手元に無いか、git が失敗した")


def make_git() -> Git:
    return Git(time.monotonic() + TIME_LIMIT)


def push_args(segment: str) -> list[str] | None:
    """1つのコマンドが git push なら、push の後ろの引数。そうでなければ None。"""
    args = git_args(segment)
    if not args or args[0] != "push":
        return None
    return args[1:]


def erasing_arg(args: list[str]) -> str | None:
    """push の引数のうち、リモートの履歴を消すもの(ブランチを消す形のほか)。"""
    for a in args:
        if a.startswith("--"):
            if a.split("=")[0] in ERASING_LONG_FLAGS:
                return a
        elif a.startswith("-"):
            if a not in DELETE_FLAGS and ("f" in a or "d" in a):
                return a
        elif a.startswith("+"):
            return a
    return None


def deleted_branches(args: list[str]) -> tuple[str | None, list[str]] | None:
    """ブランチを消す push なら、(リモート, 消すブランチ)。消す push でなければ None。"""
    positionals = []
    has_repo_flag = False
    i = 0
    while i < len(args):
        a = args[i]
        if a.split("=")[0] == "--repo":
            has_repo_flag = True
        if a in VALUE_FLAGS:
            i += 2
            continue
        if not a.startswith("-"):
            positionals.append(a)
        i += 1
    by_flag = any(a in DELETE_FLAGS for a in args)
    refspecs = positionals[1:]
    by_colon = [r for r in refspecs if r.startswith(":")]
    if not by_flag and not by_colon and not (positionals and positionals[0].startswith(":")):
        return None
    remote = positionals[0] if positionals else None
    if has_repo_flag or (remote and remote.startswith(":")):
        remote = None
    names = refspecs if by_flag else [r[1:] for r in by_colon]
    return remote, [n[len(HEADS):] if n.startswith(HEADS) else n for n in names]


def unmerged_reason(git, repo: str, remote: str | None, branches: list[str],
                    cache: dict) -> str | None:
    """消せないブランチと理由。みなマージ済みなら None。"""
    if not remote or not branches or not all(branches):
        return "消すリモートかブランチが読めず、マージ済みかを確かめられない"
    try:
        key = (repo, remote)
        if key not in cache:
            cache[key] = (git.ls_remote(repo, remote), git.default_branch(repo, remote))
        heads, default_ref = cache[key]
        default_name = default_ref.rsplit(f"refs/remotes/{remote}/", 1)[-1]
        for b in branches:
            if b == default_name:
                return f"{b}: 既定のブランチ"
            if b not in heads:
                return f"{b}: リモートに無い"
            try:
                merged = git.is_ancestor(repo, heads[b], default_ref)
            except GitFailed as e:
                return f"{b}: マージ済みかを確かめられない({e})"
            if not merged:
                return f"{b}: 既定のブランチにマージされていない"
    except GitFailed as e:
        return f"マージ済みかを確かめられない({e})"
    except Exception as e:
        return f"マージ済みかを確かめられない({type(e).__name__}: {e})"
    return None


def moves_folder(segments: list[str]) -> bool:
    for segment in segments:
        tokens = tokens_of(segment)
        if tokens and tokens[0].lower() in FOLDER_COMMANDS:
            return True
    return False


def judge(command: str, cwd: str, git) -> tuple[str, str] | None:
    """("deny", 止める文) か ("ask", 当たった引数)。ふつうの push と push 以外は None。"""
    segments = [s.strip() for s in SEPARATORS.split(command)]
    deletes = []
    asked = None
    for segment in segments:
        args = push_args(segment)
        if args is None:
            continue
        erasing = erasing_arg(args)
        if erasing:
            return "deny", (f"リモートの履歴を消す push なので止めました({erasing})。"
                            f"履歴の書き換えを頼まれたときは {LEASE} を使ってください。")
        deleted = deleted_branches(args)
        if deleted:
            if any(o.split("=")[0] in REPO_OPTIONS for o in git_options(segment)):
                return "deny", ("リモートのブランチを消す push に --git-dir か --work-tree があり、"
                                "確かめるリポジトリと push するリポジトリが別になりうるので止めました。")
            deletes.append((git_folder(segment, cwd), *deleted))
        lease = next((a for a in args if a.startswith(LEASE)), None)
        if lease and asked is None:
            asked = "ask", lease
    if deletes and moves_folder(segments):
        return "deny", ("リモートのブランチを消す push と同じコマンドにフォルダを移るコマンド"
                        "(cd・chdir・Set-Location・sl・pushd・Push-Location・popd・Pop-Location)"
                        "があり、確かめるリポジトリと"
                        "push するリポジトリが別になりうるので止めました。")
    cache = {}
    for repo, remote, branches in deletes:
        reason = unmerged_reason(git, repo, remote, branches, cache)
        if reason:
            return "deny", (f"リモートのブランチを消す push なので止めました({reason})。"
                            "消せるのは、リモートの既定のブランチにマージ済みのブランチだけです。")
    return asked


def main() -> int:
    try:
        event = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return 0
    command = (event.get("tool_input") or {}).get("command")
    if not command:
        return 0
    found = judge(command, event.get("cwd") or os.getcwd(), make_git())
    if found is None:
        return 0
    decision, text = found
    if decision == "deny":
        sys.stderr.reconfigure(encoding="utf-8")
        print(text, file=sys.stderr)
        return 2
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": f"リモートの履歴を書き換える push です({text})。",
    }}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

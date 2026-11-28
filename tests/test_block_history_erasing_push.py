"""claude/hooks/block_history_erasing_push.py が、リモートの履歴を消す push を止めるテスト。

仕様は docs/specs/block_history_erasing_push.py.md。
フックの main() を同じプロセスの中で呼び(標準入出力を差し替える)、
git を走らせる確かめは偽物に差し替えるので、small。本物の git での確かめは medium の方。
実行(この階層で): python -m unittest discover -s tests
"""
import importlib.util
import io
import json
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

HOOKS = Path(__file__).resolve().parents[1] / "claude" / "hooks"
SCRIPT = HOOKS / "block_history_erasing_push.py"
sys.path.insert(0, str(HOOKS))
spec = importlib.util.spec_from_file_location("block_history_erasing_push", SCRIPT)
bhep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bhep)


class 偽のgit:
    """リモートのブランチの先端と、既定のブランチに含まれる先端を決めておく確かめ。"""

    def __init__(self, heads=None, merged=(), fail_on=None):
        self.heads = heads if heads is not None else {"main": "m1", "a": "a1", "b": "b1",
                                                      "c": "c1", "old": "o1"}
        self.merged = set(merged) | {"m1"}
        self.fail_on = fail_on
        self.ls_remote_calls = []

    def _fail(self, name):
        if self.fail_on == name:
            raise bhep.GitFailed("git が失敗した")

    def ls_remote(self, repo, remote):
        self._fail("ls_remote")
        self.ls_remote_calls.append((repo, remote))
        return dict(self.heads)

    def default_branch(self, repo, remote):
        self._fail("default_branch")
        return f"refs/remotes/{remote}/main"

    def is_ancestor(self, repo, sha, ref):
        self._fail("is_ancestor")
        return sha in self.merged


def run_hook(tool_name, command, git=None):
    """フックを走らせ、(終了コード, 標準出力, 標準エラー) を返す。"""
    git = git or 偽のgit()
    event = json.dumps({"tool_name": tool_name, "tool_input": {"command": command},
                        "cwd": "repo"})
    saved = sys.stdin, sys.stdout, sys.stderr
    stdin = io.TextIOWrapper(io.BytesIO(event.encode("utf-8")), encoding="utf-8")
    stdout = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    stderr = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    sys.stdin, sys.stdout, sys.stderr = stdin, stdout, stderr
    try:
        with mock.patch.object(bhep, "make_git", lambda: git):
            code = bhep.main()
        stdout.flush()
        stderr.flush()
        return (code, stdout.buffer.getvalue().decode("utf-8"),
                stderr.buffer.getvalue().decode("utf-8"))
    finally:
        sys.stdin, sys.stdout, sys.stderr = saved


class リモートの履歴を消すpush(unittest.TestCase):
    def test_履歴を消すpushは当たった引数を書いて止める(self):
        cases = (("git push --force", "--force"), ("git push -f origin main", "-f"),
                 ("git push -fu origin main", "-fu"), ("git push origin +main", "+main"),
                 ("git push --mirror", "--mirror"), ("git push --prune origin", "--prune"))
        for command, arg in cases:
            for tool in ("Bash", "PowerShell"):
                with self.subTest(command=command, tool=tool):
                    code, _, err = run_hook(tool, command)
                    self.assertEqual(code, 2)
                    self.assertIn(arg, err)
        for command in ("git push origin :old", "git push --delete origin old",
                        "git push -d origin old"):
            for tool in ("Bash", "PowerShell"):
                with self.subTest(command=command, tool=tool):
                    code, _, err = run_hook(tool, command)
                    self.assertEqual(code, 2)
                    self.assertIn("old", err)
                    self.assertIn("マージされていない", err)

    def test_force_with_leaseはどの位置でも確認に回す(self):
        for command in ("git push --force-with-lease", "git push origin main --force-with-lease=main"):
            with self.subTest(command=command):
                code, out, _ = run_hook("Bash", command)
                self.assertEqual(code, 0)
                decision = json.loads(out)["hookSpecificOutput"]["permissionDecision"]
                self.assertEqual(decision, "ask")

    def test_つないだコマンドは1つずつ見て止めるpushがあれば止める(self):
        for command in ("git add . && git push -f",
                        "git status; git -C repo push origin +main",
                        "git push --force-with-lease && git push -f"):
            with self.subTest(command=command):
                self.assertEqual(run_hook("Bash", command)[0], 2)

    def test_ふつうのpushとpush以外のgitは何も返さず通す(self):
        for command in ("git push", "git push origin main", "git push -u origin feature",
                        "git push origin main:main", "git push origin main 2>&1 | Out-String",
                        "git fetch --prune", "git branch -d old", "git commit -m push"):
            with self.subTest(command=command):
                self.assertEqual(run_hook("Bash", command), (0, "", ""))


class リモートのブランチを消すpush(unittest.TestCase):
    def test_マージ済みのブランチを消すpushは通す(self):
        for command in ("git push origin --delete a", "git push -d origin a",
                        "git push origin :a", "git push origin --delete a refs/heads/b",
                        "git -C repo push origin :a :b"):
            for tool in ("Bash", "PowerShell"):
                with self.subTest(command=command, tool=tool):
                    git = 偽のgit(merged={"a1", "b1"})
                    self.assertEqual(run_hook(tool, command, git), (0, "", ""))

    def test_マージしていないブランチを消すpushは止める(self):
        for command in ("git push origin --delete a b c", "git push origin :a :b :c",
                        "git push origin --delete a && git push origin :b"):
            with self.subTest(command=command):
                code, _, err = run_hook("Bash", command, 偽のgit(merged={"a1", "c1"}))
                self.assertEqual(code, 2)
                self.assertIn("b", err)
                self.assertIn("マージされていない", err)

    def test_既定のブランチを消すpushは止める(self):
        for command in ("git push origin --delete main", "git push origin :refs/heads/main"):
            with self.subTest(command=command):
                code, _, err = run_hook("Bash", command)
                self.assertEqual(code, 2)
                self.assertIn("main", err)
                self.assertIn("既定のブランチ", err)

    def test_消すpushにほかの消す引数が混ざれば止める(self):
        cases = (("git push --force origin --delete a", "--force"),
                 ("git push origin --delete a +main", "+main"),
                 ("git push --prune origin :a", "--prune"),
                 ("git push --mirror origin :a", "--mirror"),
                 ("git push -df origin a", "-df"),
                 ("git push origin -d a -f", "-f"))
        for command, arg in cases:
            with self.subTest(command=command):
                code, _, err = run_hook("Bash", command, 偽のgit(merged={"a1"}))
                self.assertEqual(code, 2)
                self.assertIn(arg, err)

    def test_マージ済みかを確かめられなければ止める(self):
        for fail_on in ("ls_remote", "default_branch", "is_ancestor"):
            with self.subTest(fail_on=fail_on):
                git = 偽のgit(merged={"a1"}, fail_on=fail_on)
                code, _, err = run_hook("Bash", "git push origin --delete a", git)
                self.assertEqual(code, 2)
                self.assertIn("確かめられない", err)
        with self.subTest("リモートの名前が無い"):
            self.assertEqual(run_hook("Bash", "git push --delete")[0], 2)
        with self.subTest("時間切れ"):
            git = bhep.Git(deadline=time.monotonic() - 1)
            with mock.patch.object(bhep.subprocess, "run") as run:
                with self.assertRaises(bhep.GitFailed):
                    git.ls_remote("repo", "origin")
                run.assert_not_called()

    def test_消すpushと同じコマンドにcdがあれば止める(self):
        for command in ("cd ../other && git push origin --delete a",
                        "Set-Location ../other; git push origin :a",
                        "pushd ../other && git push -d origin a",
                        "git push origin --delete a; Push-Location ../other"):
            with self.subTest(command=command):
                code, _, err = run_hook("Bash", command, 偽のgit(merged={"a1"}))
                self.assertEqual(code, 2)
                self.assertIn("フォルダを移る", err)

    def test_いくつものブランチを消してもls_remoteはリモートごとに1回(self):
        git = 偽のgit(merged={"a1", "b1", "c1"})
        command = "git push origin --delete a b && git push origin :c && git push upstream :a"
        self.assertEqual(run_hook("Bash", command, git), (0, "", ""))
        self.assertEqual(sorted(git.ls_remote_calls), [("repo", "origin"), ("repo", "upstream")])


if __name__ == "__main__":
    unittest.main()

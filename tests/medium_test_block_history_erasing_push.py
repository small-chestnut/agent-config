"""claude/hooks/block_history_erasing_push.py が、本物の git で、マージ済みのブランチを消す push だけを通すテスト。

仕様は docs/specs/block_history_erasing_push.py.md。
一時フォルダに裸のリモートと clone を作り、フックを別のプロセスで走らせるので、medium。
実行(この階層で): python -m unittest tests/medium_test_block_history_erasing_push.py
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "claude" / "hooks" / "block_history_erasing_push.py"


class リモートのブランチを本物のgitで消す(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        empty_config = root / "gitconfig"
        empty_config.write_text("", encoding="utf-8")
        self.env = dict(os.environ, GIT_CONFIG_GLOBAL=str(empty_config), GIT_CONFIG_NOSYSTEM="1",
                        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
                        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")
        self.remote = root / "remote.git"
        self.git(root, "init", "--bare", "-b", "main", str(self.remote))
        self.work = root / "work"
        self.git(root, "clone", str(self.remote), str(self.work))
        self.git(self.work, "commit", "--allow-empty", "-m", "first")
        self.git(self.work, "push", "origin", "main")
        self.git(self.work, "remote", "set-head", "origin", "main")

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, cwd, *args):
        subprocess.run(["git", *args], cwd=cwd, env=self.env, check=True,
                       capture_output=True)

    def add_branch(self, cwd, name, merge):
        self.git(cwd, "switch", "-c", name, "main")
        self.git(cwd, "commit", "--allow-empty", "-m", name)
        self.git(cwd, "push", "origin", name)
        self.git(cwd, "switch", "main")
        if merge:
            self.git(cwd, "merge", "--no-ff", "-m", f"merge {name}", name)
            self.git(cwd, "push", "origin", "main")
            self.git(cwd, "fetch", "origin")

    def run_hook(self, command):
        event = json.dumps({"tool_name": "Bash", "tool_input": {"command": command},
                            "cwd": str(self.work)})
        return subprocess.run([sys.executable, str(SCRIPT)], input=event.encode("utf-8"),
                              env=self.env, capture_output=True, timeout=60)

    def remote_heads(self):
        out = subprocess.run(["git", "ls-remote", "--heads", str(self.remote)], env=self.env,
                             check=True, capture_output=True, text=True).stdout
        return {line.split("\trefs/heads/")[1] for line in out.splitlines()}

    def test_マージ済みのブランチはリモートから消せる(self):
        self.add_branch(self.work, "done", merge=True)
        command = "git push origin --delete done"
        result = self.run_hook(command)
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
        self.git(self.work, "push", "origin", "--delete", "done")
        self.assertEqual(self.remote_heads(), {"main"})

    def test_マージしていないブランチはリモートから消せない(self):
        self.add_branch(self.work, "done", merge=True)
        self.add_branch(self.work, "wip", merge=False)
        result = self.run_hook("git push origin --delete done wip")
        self.assertEqual(result.returncode, 2)
        self.assertIn("wip", result.stderr.decode("utf-8"))

    def test_手元に無いコミットを持つブランチはリモートから消せない(self):
        self.add_branch(self.work, "done", merge=True)
        other = Path(self.tmp.name) / "other"
        self.git(Path(self.tmp.name), "clone", str(self.remote), str(other))
        self.git(other, "switch", "done")
        self.git(other, "commit", "--allow-empty", "-m", "later")
        self.git(other, "push", "origin", "done")
        result = self.run_hook("git push origin :done")
        self.assertEqual(result.returncode, 2)
        self.assertIn("done", result.stderr.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()

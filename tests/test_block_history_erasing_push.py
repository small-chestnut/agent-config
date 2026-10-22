"""claude/hooks/block_history_erasing_push.py が、リモートの履歴を消す push を止めるテスト。

実行(この階層で): python -m unittest discover -s tests
"""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "claude" / "hooks" / "block_history_erasing_push.py"
spec = importlib.util.spec_from_file_location("block_history_erasing_push", SCRIPT)
bhep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bhep)


class リモートの履歴を消すpush(unittest.TestCase):
    def test_ふつうのpushは通す(self):
        for command in ("git push", "git push origin main", "git push -u origin feature",
                        "git push origin main:main", "git push origin main 2>&1 | Out-String"):
            self.assertIsNone(bhep.judge(command), command)

    def test_強制と削除のpushは止める(self):
        for command in ("git push --force", "git push -f origin main", "git push -fu origin main",
                        "git push origin +main", "git push origin :old", "git push --delete origin old",
                        "git push -d origin old", "git push --mirror", "git push --prune origin"):
            self.assertEqual(bhep.judge(command)[0], "deny", command)

    def test_force_with_leaseはどの位置でも確認に回す(self):
        for command in ("git push --force-with-lease", "git push origin main --force-with-lease=main"):
            self.assertEqual(bhep.judge(command)[0], "ask", command)

    def test_つないだコマンドの中のpushも見る(self):
        self.assertEqual(bhep.judge("git add . && git push -f")[0], "deny")
        self.assertEqual(bhep.judge("git status; git -C repo push origin +main")[0], "deny")

    def test_push以外のgitは止めない(self):
        for command in ("git fetch --prune", "git branch -d old", "git commit -m push"):
            self.assertIsNone(bhep.judge(command), command)


class コマンドを走らせる前の動き(unittest.TestCase):
    def run_hook(self, tool_name, command):
        event = json.dumps({"tool_name": tool_name, "tool_input": {"command": command}})
        return subprocess.run([sys.executable, str(SCRIPT)], input=event.encode("utf-8"),
                              capture_output=True)

    def test_強制pushは理由を返して止める(self):
        r = self.run_hook("PowerShell", "git push -fu origin main")
        self.assertEqual(r.returncode, 2)
        self.assertIn("-fu", r.stderr.decode("utf-8"))

    def test_force_with_leaseは確認を求める(self):
        r = self.run_hook("Bash", "git push origin main --force-with-lease")
        self.assertEqual(r.returncode, 0)
        out = json.loads(r.stdout.decode("utf-8"))["hookSpecificOutput"]
        self.assertEqual(out["permissionDecision"], "ask")

    def test_ふつうのpushは何も返さず通す(self):
        r = self.run_hook("Bash", "git push origin main")
        self.assertEqual((r.returncode, r.stdout), (0, b""))


if __name__ == "__main__":
    unittest.main()

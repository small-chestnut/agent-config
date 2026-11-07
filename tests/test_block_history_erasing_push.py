"""claude/hooks/block_history_erasing_push.py が、リモートの履歴を消す push を止めるテスト。

仕様は docs/specs/block_history_erasing_push.py.md。
フックの main() を同じプロセスの中で呼ぶ(標準入出力を差し替える)ので、小。
実行(この階層で): python -m unittest discover -s tests
"""
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "claude" / "hooks" / "block_history_erasing_push.py"
spec = importlib.util.spec_from_file_location("block_history_erasing_push", SCRIPT)
bhep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bhep)


def run_hook(tool_name, command):
    """フックを走らせ、(終了コード, 標準出力, 標準エラー) を返す。"""
    event = json.dumps({"tool_name": tool_name, "tool_input": {"command": command}})
    saved = sys.stdin, sys.stdout, sys.stderr
    stdin = io.TextIOWrapper(io.BytesIO(event.encode("utf-8")), encoding="utf-8")
    stdout = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    stderr = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    sys.stdin, sys.stdout, sys.stderr = stdin, stdout, stderr
    try:
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
                 ("git push origin :old", ":old"), ("git push --delete origin old", "--delete"),
                 ("git push -d origin old", "-d"), ("git push --mirror", "--mirror"),
                 ("git push --prune origin", "--prune"))
        for command, arg in cases:
            for tool in ("Bash", "PowerShell"):
                with self.subTest(command=command, tool=tool):
                    code, _, err = run_hook(tool, command)
                    self.assertEqual(code, 2)
                    self.assertIn(arg, err)

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


if __name__ == "__main__":
    unittest.main()

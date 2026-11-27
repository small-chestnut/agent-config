"""claude/hooks/block_new_branch_worktree.py が、新しいブランチの worktree を git で作るのを止めるテスト。

仕様は docs/specs/block_new_branch_worktree.py.md。
フックの main() を同じプロセスの中で呼ぶ(標準入出力を差し替える)ので、small。
実行(この階層で): python -m unittest discover -s tests
"""
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "claude" / "hooks"
SCRIPT = HOOKS / "block_new_branch_worktree.py"
sys.path.insert(0, str(HOOKS))
spec = importlib.util.spec_from_file_location("block_new_branch_worktree", SCRIPT)
bnbw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bnbw)


def run_hook(tool_name, command):
    """フックを走らせ、(終了コード, 標準出力, 標準エラー) を返す。"""
    event = json.dumps({"tool_name": tool_name, "tool_input": {"command": command}})
    saved = sys.stdin, sys.stdout, sys.stderr
    stdin = io.TextIOWrapper(io.BytesIO(event.encode("utf-8")), encoding="utf-8")
    stdout = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    stderr = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    sys.stdin, sys.stdout, sys.stderr = stdin, stdout, stderr
    try:
        code = bnbw.main()
        stdout.flush()
        stderr.flush()
        return (code, stdout.buffer.getvalue().decode("utf-8"),
                stderr.buffer.getvalue().decode("utf-8"))
    finally:
        sys.stdin, sys.stdout, sys.stderr = saved


class 新しいブランチのworktree(unittest.TestCase):
    def test_新しいブランチを作るworktree_addは止めてアプリに作らせるよう返す(self):
        for command in ("git worktree add -b feature ../wt",
                        "git worktree add ../wt -B feature main",
                        "git worktree add -bfeature ../wt",
                        "git worktree add ../wt",
                        "git -C repo worktree add -b feature ../wt",
                        "git fetch && git worktree add -b feature ../wt origin/main",
                        "git worktree add ../wt 2>&1",
                        "git worktree add ../wt > log.txt",
                        "git worktree add ../wt >log.txt",
                        "git worktree add ../wt 2>&1 | Out-String"):
            for tool in ("Bash", "PowerShell"):
                with self.subTest(command=command, tool=tool):
                    code, _, err = run_hook(tool, command)
                    self.assertEqual(code, 2)
                    self.assertIn("start_session の use_worktree: true でアプリに作らせ", err)

    def test_止めたときに返す文は使い回されたフォルダをそのまま使うこととほかのPCの作り方を伝える(self):
        for command in ("git worktree add -b feature ../wt",
                        "git worktree add -b feature ../wt origin/feature"):
            with self.subTest(command=command):
                code, _, err = run_hook("Bash", command)
                self.assertEqual(code, 2)
                self.assertIn("アプリがほかのタスクのフォルダを使い回しても、そのまま使ってください", err)
                self.assertIn("ほかの PC から続けるタスクは、git fetch の後に "
                              "git worktree add <フォルダ> <作業ブランチ> で作ってください", err)

    def test_既にあるブランチかdetachのworktree_addは通す(self):
        for command in ("git worktree add ../wt feature",
                        "git -C repo worktree add ../wt origin/feature",
                        "git worktree add --detach ../wt",
                        "git worktree add -d ../wt main",
                        "git worktree add --lock --reason why ../wt feature"):
            with self.subTest(command=command):
                self.assertEqual(run_hook("Bash", command), (0, "", ""))
        # --reason の値はフォルダに数えないので、残りがフォルダだけなら止まる
        self.assertEqual(run_hook("Bash", "git worktree add --lock --reason why ../wt")[0], 2)

    def test_worktree_add以外のコマンドは通す(self):
        for command in ("git worktree list", "git push", "echo git worktree add -b feature ../wt"):
            with self.subTest(command=command):
                self.assertEqual(run_hook("Bash", command), (0, "", ""))


if __name__ == "__main__":
    unittest.main()

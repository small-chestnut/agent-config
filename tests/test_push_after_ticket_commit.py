"""claude/hooks/push_after_ticket_commit.py が、チケットのコミットの後に push するテスト。

仕様は docs/specs/push_after_ticket_commit.py.md。
git は関数の引数で差し替える(偽の git)ので、1つのプロセスのメモリだけで終わる小。
実行(この階層で): python -m unittest discover -s tests
"""
import importlib.util
import os
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "claude" / "hooks" / "push_after_ticket_commit.py"
spec = importlib.util.spec_from_file_location("push_after_ticket_commit", SCRIPT)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

TICKET = "# 0001-x\n\nステータス: 実装中\n"
NOT_TICKET = "# メモ\n"
LATE_STATUS = "1\n2\n3\n4\n5\nステータス: 実装中\n"


class 偽のgit:
    """呼ばれた (引数, 作業ツリー) を記録し、リポジトリの状態を答える。"""

    def __init__(self, changed=(("M", "docs/tasks/0001-x.md"),), files=None, branch="work",
                 remotes=("origin",), upstream=True, push_result=(0, "")):
        self.changed, self.branch, self.remotes = changed, branch, remotes
        self.files = {"HEAD:docs/tasks/0001-x.md": TICKET} if files is None else files
        self.upstream, self.push_result = upstream, push_result
        self.calls = []

    def __call__(self, args, cwd):
        self.calls.append((args, cwd))
        if args[0] == "symbolic-ref":
            return (0, self.branch) if self.branch else (1, "")
        if args[0] == "diff-tree":
            return 0, "\n".join(f"{s}\t{p}" for s, p in self.changed)
        if args[0] == "show":
            text = self.files.get(args[1])
            return (0, text) if text is not None else (128, "fatal")
        if args[0] == "remote":
            return 0, "\n".join(self.remotes)
        if args[0] == "rev-parse":
            return (0, "origin/work") if self.upstream else (128, "fatal")
        if args[0] == "push":
            return self.push_result
        raise AssertionError(args)

    def pushes(self):
        return [(a, c) for a, c in self.calls if a[0] == "push"]


CWD = os.path.join(os.sep, "repo")


def run(command, git, tool="Bash"):
    event = {"tool_name": tool, "tool_input": {"command": command}, "cwd": CWD}
    return hook.push_message(event, git)


class チケットのコミットの後のpush(unittest.TestCase):
    def test_チケットを足したコミットの後に作業ブランチをpushする(self):
        git = 偽のgit(changed=(("A", "docs/tasks/0001-x.md"),))
        message = run("git commit -m y", git)
        self.assertEqual(git.pushes(), [(["push"], CWD)])
        self.assertEqual(message, "チケットのコミットを origin/work へ push した。")

    def test_git_Cで指した作業ツリーのHEADを見てpushする(self):
        git = 偽のgit()
        run("git -C x commit -m y", git)
        self.assertEqual(git.pushes(), [(["push"], os.path.join(CWD, "x"))])
        self.assertTrue(all(c == os.path.join(CWD, "x") for _, c in git.calls))

    def test_cdで移った作業ツリーのHEADを見てpushする(self):
        git = 偽のgit()
        run('cd "x" && git commit -m y', git)
        self.assertEqual(git.pushes(), [(["push"], os.path.join(CWD, "x"))])
        git = 偽のgit()
        run("Set-Location 'y'; cd z; git commit -m y", git)
        self.assertEqual(git.pushes(), [(["push"], os.path.join(CWD, "z"))])

    def test_チケットを消したコミットの後にもpushする(self):
        git = 偽のgit(changed=(("D", "docs/tasks/0001-x.md"),),
                      files={"HEAD~1:docs/tasks/0001-x.md": TICKET})
        run("git commit -m y", git)
        self.assertEqual(len(git.pushes()), 1)

    def test_ステータスの行が冒頭5行目にあるmdはチケットと見る(self):
        git = 偽のgit(files={"HEAD:docs/tasks/0001-x.md": "1\n2\n3\n4\nステータス: 実装中\n"})
        run("git commit -m y", git)
        self.assertEqual(len(git.pushes()), 1)

    def test_ステータスの行が6行目にあるmdはチケットと見ない(self):
        git = 偽のgit(files={"HEAD:docs/tasks/0001-x.md": LATE_STATUS})
        self.assertIsNone(run("git commit -m y", git))
        self.assertEqual(git.pushes(), [])

    def test_上流の無いブランチではリモートとHEADを指してpushする(self):
        git = 偽のgit(upstream=False)
        message = run("git commit -m y", git)
        self.assertEqual(git.pushes(), [(["push", "-u", "origin", "HEAD"], CWD)])
        self.assertEqual(message, "チケットのコミットを origin/work へ push した。")

    def test_originが無ければgit_remoteの1行目のリモートへpushする(self):
        git = 偽のgit(upstream=False, remotes=("backup", "other"))
        run("git commit -m y", git)
        self.assertEqual(git.pushes(), [(["push", "-u", "backup", "HEAD"], CWD)])

    def test_チケットに触れないコミットの後にはpushしない(self):
        git = 偽のgit(changed=(("M", "src/a.py"),))
        self.assertIsNone(run("git commit -m y", git))
        git = 偽のgit(changed=(("M", "docs/memo.md"),), files={"HEAD:docs/memo.md": NOT_TICKET})
        self.assertIsNone(run("git commit -m y", git))
        self.assertEqual(git.pushes(), [])

    def test_リモートの無いリポジトリではpushしない(self):
        git = 偽のgit(remotes=())
        self.assertIsNone(run("git commit -m y", git))
        self.assertEqual(git.pushes(), [])

    def test_ブランチに居ないHEADではpushしない(self):
        git = 偽のgit(branch="")
        self.assertIsNone(run("git commit -m y", git))
        self.assertEqual(git.pushes(), [])

    def test_git_commitでないコマンドの後には何もしない(self):
        for command in ("git status", "git push", "ls"):
            git = 偽のgit()
            self.assertIsNone(run(command, git))
            self.assertEqual(git.calls, [])
        git = 偽のgit()
        self.assertIsNone(hook.push_message({"tool_name": "Read", "tool_input": {"command": "git commit"}}, git))
        self.assertEqual(git.calls, [])

    def test_pushに失敗したらgitの出力をClaudeに知らせる(self):
        git = 偽のgit(push_result=(1, "rejected: non-fast-forward"))
        message = run("git commit -m y", git)
        self.assertEqual(message, "チケットのコミットの push に失敗した:\nrejected: non-fast-forward")


if __name__ == "__main__":
    unittest.main()

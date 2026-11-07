"""claude/hooks/check_rule_documents_changed_by_shell.py が、シェルで書き換えた決まりの文書を数え、問い返すテスト。

実行(この階層で): python -m unittest discover -s tests
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "claude" / "hooks"
SCRIPT = HOOKS / "check_rule_documents_changed_by_shell.py"
sys.path.insert(0, str(HOOKS))
spec = importlib.util.spec_from_file_location("check_rule_documents_changed_by_shell", SCRIPT)
shell = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shell)

LONG = "- " + "あ" * 61


class コマンドに書かれたパス(unittest.TestCase):
    def test_ドライブ文字のパスを拾う(self):
        paths = shell.paths_in_command('cd "E:/Dropbox/root/projects/gemini" && python x.py')
        self.assertIn(Path("E:/Dropbox/root/projects/gemini"), paths)

    def test_Git_Bash_の形のパスをドライブ文字に直す(self):
        self.assertIn(Path("C:/Users/Reo/dev"), shell.paths_in_command("ls /c/Users/Reo/dev"))

    def test_ホームからのパスを拾う(self):
        self.assertIn(Path.home() / "dev/projects", shell.paths_in_command("cd ~/dev/projects && ls"))


class 足された行(unittest.TestCase):
    def test_足した行と書き換えた行の番号を返す(self):
        self.assertEqual(shell.added_lines("- a\n- b\n", "- a\n- B\n- c\n"), {2, 3})

    def test_消しただけなら足された行は無い(self):
        self.assertEqual(shell.added_lines("- a\n- b\n", "- a\n"), set())

    def test_コードブロックの中と空の行は問わない(self):
        text = "- 足した\n\n```\n- コード\n```\n"
        self.assertEqual(shell.asked_lines(text, {1, 2, 4}), [(1, "- 足した")])


class 取り込むコマンド(unittest.TestCase):
    def test_取り込むgitのコマンドを見分ける(self):
        for command in ("git merge --ff-only origin/main", "git -C x pull", "cd a && git checkout main",
                        "git cherry-pick abc"):
            self.assertTrue(shell.brings_other_commits(command), command)

    def test_取り込まないコマンドは見分けない(self):
        for command in ("git commit -am x", "git add .", "git stash pop", "git log --grep merge",
                        "git merge-base a b", "python edit.py"):
            self.assertFalse(shell.brings_other_commits(command), command)


class 取り込んだ行(unittest.TestCase):
    def test_衝突の印の行は取り込んだ行に数える(self):
        text = "<<<<<<< HEAD\n- a\n=======\n- b\n>>>>>>> other\n"
        self.assertEqual(shell.imported_lines(text, []), {1, 3, 5})

    def test_印に似た行は取り込んだ行に数えない(self):
        text = "========\n- =======\n<<<<<<<x\n"
        self.assertEqual(shell.imported_lines(text, []), set())

    def test_どれかの版と同じ行は取り込んだ行に数える(self):
        self.assertEqual(shell.imported_lines("- a\n- b\n- c\n", ["- a\n- c\n", "- b\n"]), {1, 2, 3})
        self.assertEqual(shell.imported_lines("- a\n- b\n- c\n", ["- a\n"]), {1})


class コマンドの前後の動き(unittest.TestCase):
    """一時的な git リポジトリで、before と after をフックとして走らせる。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        for args in (["init", "-q"], ["config", "user.email", "t@example.com"],
                     ["config", "user.name", "t"]):
            subprocess.run(["git", *args], cwd=self.root, check=True)
        self.doc = self.root / "CLAUDE.md"
        self.doc.write_text(f"{LONG}\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=self.root, check=True)
        self.event = {"session_id": "test", "tool_use_id": f"id-{id(self)}", "tool_name": "Bash",
                      "cwd": str(Path.home()), "tool_input": {"command": f'cd "{self.root.as_posix()}" && python edit.py'}}

    def tearDown(self):
        shell.snapshot_path(self.event).unlink(missing_ok=True)
        self.tmp.cleanup()

    def run_hook(self, mode):
        return subprocess.run([sys.executable, str(SCRIPT), mode], input=json.dumps(self.event).encode("utf-8"),
                              capture_output=True)

    def test_コマンドで長い決まりを足すと知らせと問いが返る(self):
        self.assertEqual(self.run_hook("before").returncode, 0)
        self.doc.write_text(f"{LONG}\n{LONG}\n", encoding="utf-8")
        r = self.run_hook("after")
        self.assertEqual(r.returncode, 2)
        err = r.stderr.decode("utf-8")
        self.assertIn("CLAUDE.md:2  61字", err)
        self.assertIn("消しても意味が変わらない語", err)
        self.assertNotIn("CLAUDE.md:1", err)

    def test_コマンドの前からあった変更は問わない(self):
        self.doc.write_text(f"{LONG}\n- 前の変更\n", encoding="utf-8")
        self.run_hook("before")
        self.assertEqual(self.run_hook("after").returncode, 0)

    def test_コマンドで作った決まりの文書も数える(self):
        self.run_hook("before")
        skill = self.root / ".claude" / "skills" / "x" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(f"{LONG}\n", encoding="utf-8")
        r = self.run_hook("after")
        self.assertEqual(r.returncode, 2)
        self.assertIn(".claude/skills/x/SKILL.md:1", r.stderr.decode("utf-8"))

    def test_決まりの文書でなければ問わない(self):
        self.run_hook("before")
        (self.root / "README.md").write_text(f"{LONG}\n", encoding="utf-8")
        self.assertEqual(self.run_hook("after").returncode, 0)

    def test_写しが無ければ何もしない(self):
        self.doc.write_text(f"{LONG}\n{LONG}\n", encoding="utf-8")
        self.assertEqual(self.run_hook("after").returncode, 0)

    def git(self, *args, check=True):
        return subprocess.run(["git", *args], cwd=self.root, check=check, capture_output=True)

    def set_command(self, command):
        self.event["tool_input"]["command"] = f'cd "{self.root.as_posix()}" && {command}'

    def other_branch_with_long_line(self):
        """別のブランチに長い行を足してコミットし、元のブランチに戻る。"""
        self.git("checkout", "-q", "-b", "other")
        self.doc.write_text(f"{LONG}\n{LONG}\n", encoding="utf-8")
        self.git("commit", "-qam", "other")
        self.git("checkout", "-q", "-")

    def test_早送りで取り込んだ行は問わない(self):
        self.other_branch_with_long_line()
        self.set_command("git merge --ff-only other")
        self.run_hook("before")
        self.git("merge", "--ff-only", "other")
        self.assertEqual(self.run_hook("after").returncode, 0)

    def test_取り込むコマンドの後に書いた行は問う(self):
        self.other_branch_with_long_line()
        self.set_command("git merge --ff-only other && python edit.py")
        self.run_hook("before")
        self.git("merge", "--ff-only", "other")
        self.doc.write_text("\n".join([LONG] * 3) + "\n", encoding="utf-8")
        r = self.run_hook("after")
        self.assertEqual(r.returncode, 2)
        err = r.stderr.decode("utf-8")
        self.assertIn("CLAUDE.md:3", err)
        self.assertNotIn("CLAUDE.md:2", err)

    def test_衝突した取り込みでは衝突の印と両方の行を問わない(self):
        self.git("checkout", "-q", "-b", "other")
        self.doc.write_text("- " + "い" * 61 + "\n", encoding="utf-8")
        self.git("commit", "-qam", "other")
        self.git("checkout", "-q", "-")
        self.doc.write_text("- " + "う" * 61 + "\n", encoding="utf-8")
        self.git("commit", "-qam", "main")
        self.set_command("git merge other")
        self.run_hook("before")
        self.assertNotEqual(self.git("merge", "other", check=False).returncode, 0)
        self.assertIn("<<<<<<<", self.doc.read_text(encoding="utf-8"))
        self.assertEqual(self.run_hook("after").returncode, 0)

    def test_取り込まないコマンドでコミットした行は問う(self):
        self.set_command("python edit.py && git commit -qam x")
        self.run_hook("before")
        self.doc.write_text(f"{LONG}\n{LONG}\n", encoding="utf-8")
        self.git("commit", "-qam", "x")
        r = self.run_hook("after")
        self.assertEqual(r.returncode, 2)
        self.assertIn("CLAUDE.md:2", r.stderr.decode("utf-8"))

    def test_変更を捨ててHEADに戻した行は問わない(self):
        self.doc.write_text("- 前の変更\n", encoding="utf-8")
        self.set_command("git restore CLAUDE.md")
        self.run_hook("before")
        self.git("restore", "CLAUDE.md")
        self.assertEqual(self.run_hook("after").returncode, 0)


if __name__ == "__main__":
    unittest.main()

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


if __name__ == "__main__":
    unittest.main()

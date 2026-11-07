"""claude/hooks/check_rule_documents_changed_by_shell.py が、シェルで書き換えたプロンプトを数え、問い返すテスト。

実行(この階層で): python -m unittest discover -s tests
"""
import hashlib
import importlib.util
import json
import re
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


class 取り込むgitコマンド(unittest.TestCase):
    def test_取り込むgitコマンドを見分ける(self):
        for command in ("git merge --ff-only origin/main", "git -C x pull", "cd a && git checkout main",
                        "git cherry-pick abc"):
            self.assertTrue(shell.brings_other_commits(command), command)

    def test_取り込まないコマンドは見分けない(self):
        for command in ("git commit -am x", "git add .", "git stash pop", "git log --grep merge",
                        "git merge-base a b", "python edit.py"):
            self.assertFalse(shell.brings_other_commits(command), command)


class 取り込んだ行(unittest.TestCase):
    def test_コンフリクトマーカーの行は取り込んだ行に数える(self):
        text = "<<<<<<< HEAD\n- a\n=======\n- b\n>>>>>>> other\n"
        self.assertEqual(shell.imported_lines(text, []), {1, 3, 5})

    def test_コンフリクトマーカーに似た行は取り込んだ行に数えない(self):
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
        key = hashlib.sha256(f"test:edit-1-{self.event['tool_use_id']}".encode("utf-8")).hexdigest()[:16]
        for p in shell.WRITTEN_DIR.glob(f"*-{key}*.json"):
            p.unlink(missing_ok=True)
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

    def test_コマンドで足した行はプロンプトに足した行と知らせる(self):
        self.run_hook("before")
        self.doc.write_text(f"{LONG}\n{LONG}\n", encoding="utf-8")
        r = self.run_hook("after")
        self.assertIn("このコマンドでプロンプトに足した行です。", r.stderr.decode("utf-8"))

    def test_コマンドの前からあった変更は問わない(self):
        self.doc.write_text(f"{LONG}\n- 前の変更\n", encoding="utf-8")
        self.run_hook("before")
        self.assertEqual(self.run_hook("after").returncode, 0)

    def test_コマンドで作ったプロンプトも数える(self):
        self.run_hook("before")
        skill = self.root / ".claude" / "skills" / "x" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(f"{LONG}\n", encoding="utf-8")
        r = self.run_hook("after")
        self.assertEqual(r.returncode, 2)
        self.assertIn(".claude/skills/x/SKILL.md:1", r.stderr.decode("utf-8"))

    def test_プロンプトでなければ問わない(self):
        self.run_hook("before")
        (self.root / "README.md").write_text(f"{LONG}\n", encoding="utf-8")
        self.assertEqual(self.run_hook("after").returncode, 0)

    def test_スナップショットが無ければ何もしない(self):
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

    def test_取り込むgitコマンドの後に書いた行は問う(self):
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

    def test_コンフリクトした取り込みではコンフリクトマーカーと両方の行を問わない(self):
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

    def edit_event(self, tool_name, tool_input, n=1):
        """Edit・Write・MultiEdit の event。n 番目の呼び出し。"""
        return {"session_id": "test", "tool_use_id": f"edit-{n}-{self.event['tool_use_id']}", "tool_name": tool_name,
                "cwd": str(self.root), "tool_input": tool_input}

    def run_edit_hook(self, mode, event):
        return subprocess.run([sys.executable, str(SCRIPT), mode], input=json.dumps(event).encode("utf-8"),
                              capture_output=True)

    def write_with(self, tool_name, tool_input, path, new_text, confirm=True):
        """Claude Code が Edit などを走らせる順(record → 書き換え → confirm)。"""
        event = self.edit_event(tool_name, tool_input)
        self.assertEqual(self.run_edit_hook("record", event).returncode, 0)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new_text, encoding="utf-8")
        if confirm:
            self.assertEqual(self.run_edit_hook("confirm", event).returncode, 0)

    def test_コマンドの間にEditで足された行は問わない(self):
        other = "- " + "い" * 61
        self.run_hook("before")
        self.write_with("Edit", {"file_path": str(self.doc), "old_string": LONG, "new_string": f"{LONG}\n{other}"},
                        self.doc, f"{LONG}\n{other}\n")
        self.assertEqual(self.run_hook("after").returncode, 0)

    def test_コマンドで足した行はEditで足された行と並んでも問う(self):
        edited, ran = "- " + "い" * 61, "- " + "う" * 61
        self.run_hook("before")
        self.write_with("Edit", {"file_path": str(self.doc), "old_string": LONG, "new_string": f"{LONG}\n{edited}"},
                        self.doc, f"{LONG}\n{edited}\n")
        self.doc.write_text(f"{LONG}\n{edited}\n{ran}\n", encoding="utf-8")
        r = self.run_hook("after")
        self.assertEqual(r.returncode, 2)
        err = r.stderr.decode("utf-8")
        self.assertIn("CLAUDE.md:3", err)
        self.assertNotIn("CLAUDE.md:2", err)

    def test_Writeで作られたプロンプトの行は問わない(self):
        skill = self.root / ".claude" / "skills" / "x" / "SKILL.md"
        self.run_hook("before")
        self.write_with("Write", {"file_path": str(skill), "content": f"{LONG}\n"}, skill, f"{LONG}\n")
        self.assertEqual(self.run_hook("after").returncode, 0)

    def test_MultiEditで書かれた行は問わない(self):
        one, two = "- " + "い" * 61, "- " + "う" * 61
        edits = [{"old_string": LONG, "new_string": f"{LONG}\n{one}"}, {"old_string": one, "new_string": two}]
        self.run_hook("before")
        self.write_with("MultiEdit", {"file_path": str(self.doc), "edits": edits}, self.doc, f"{LONG}\n{two}\n")
        self.assertEqual(self.run_hook("after").returncode, 0)

    def test_別のファイルにEditで書かれた行と同じ行をコマンドで足すと問う(self):
        line = "- " + "い" * 61
        skill = self.root / ".claude" / "skills" / "x" / "SKILL.md"
        self.run_hook("before")
        self.write_with("Edit", {"file_path": str(self.doc), "old_string": LONG, "new_string": f"{LONG}\n{line}"},
                        self.doc, f"{LONG}\n{line}\n")
        skill.parent.mkdir(parents=True)
        skill.write_text(f"{line}\n", encoding="utf-8")
        r = self.run_hook("after")
        self.assertEqual(r.returncode, 2)
        err = r.stderr.decode("utf-8")
        self.assertIn(".claude/skills/x/SKILL.md:1", err)
        self.assertNotIn("CLAUDE.md:2", err)

    def test_書けなかったEditの行はコマンドで足すと問う(self):
        line = "- " + "い" * 61
        self.run_hook("before")
        event = self.edit_event("Edit", {"file_path": str(self.doc), "old_string": LONG, "new_string": f"{LONG}\n{line}"})
        self.assertEqual(self.run_edit_hook("record", event).returncode, 0)
        self.doc.write_text(f"{LONG}\n{line}\n", encoding="utf-8")
        r = self.run_hook("after")
        self.assertEqual(r.returncode, 2)
        self.assertIn("CLAUDE.md:2", r.stderr.decode("utf-8"))

    def test_EditWriteMultiEditでは知らせず書き込みを止めない(self):
        line = "- " + "い" * 61
        event = self.edit_event("Edit", {"file_path": str(self.doc), "old_string": LONG, "new_string": f"{LONG}\n{line}"})
        for mode in ("record", "confirm"):
            r = self.run_edit_hook(mode, event)
            self.assertEqual((r.returncode, r.stderr), (0, b""), mode)

    def test_Git_Bashの形のパスのリポジトリも見る(self):
        posix = self.root.as_posix()
        if not re.match(r"^[A-Za-z]:/", posix):
            self.skipTest("ドライブ文字の無い環境")
        self.event["tool_input"]["command"] = f'cd "/{posix[0].lower()}{posix[2:]}" && python edit.py'
        self.run_hook("before")
        self.doc.write_text(f"{LONG}\n{LONG}\n", encoding="utf-8")
        self.assertEqual(self.run_hook("after").returncode, 2)

    def test_ホームからのパスのリポジトリも見る(self):
        try:
            rel = self.root.relative_to(Path.home().resolve()).as_posix()
        except ValueError:
            self.skipTest("一時フォルダがホームの下に無い環境")
        self.event["tool_input"]["command"] = f"cd ~/{rel} && python edit.py"
        self.run_hook("before")
        self.doc.write_text(f"{LONG}\n{LONG}\n", encoding="utf-8")
        self.assertEqual(self.run_hook("after").returncode, 2)

    def test_コマンドで書き換えた行も問う(self):
        self.run_hook("before")
        self.doc.write_text("- " + "い" * 61 + "\n", encoding="utf-8")
        r = self.run_hook("after")
        self.assertEqual(r.returncode, 2)
        self.assertIn("CLAUDE.md:1", r.stderr.decode("utf-8"))

    def test_コマンドで消しただけなら問わない(self):
        self.doc.write_text(f"{LONG}\n- 消す\n", encoding="utf-8")
        self.git("commit", "-qam", "two")
        self.run_hook("before")
        self.doc.write_text(f"{LONG}\n", encoding="utf-8")
        self.assertEqual(self.run_hook("after").returncode, 0)

    def test_空の行とコードブロックの中は問わない(self):
        self.run_hook("before")
        self.doc.write_text(f"{LONG}\n- 足した\n\n```\n- コード\n```\n", encoding="utf-8")
        r = self.run_hook("after")
        self.assertEqual(r.returncode, 2)
        err = r.stderr.decode("utf-8")
        self.assertIn("CLAUDE.md:2", err)
        for n in (3, 5):
            self.assertNotIn(f"CLAUDE.md:{n}", err)


if __name__ == "__main__":
    unittest.main()

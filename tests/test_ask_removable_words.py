"""claude/hooks/ask_removable_words.py が、この保存で足した行を並べて問い返すテスト。

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
SCRIPT = HOOKS / "ask_removable_words.py"
sys.path.insert(0, str(HOOKS))
spec = importlib.util.spec_from_file_location("ask_removable_words", SCRIPT)
arw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arw)


class 問う行(unittest.TestCase):
    def test_足した行のうちこの保存で書いた行を問う(self):
        text = "- 前からある\n- 足した\n- 別の保存で足した\n"
        self.assertEqual(arw.asked_lines(text, {2, 3}, "- 足した"), [(2, "- 足した")])

    def test_書いた文字列が行の一部でもその行を問う(self):
        self.assertEqual(arw.asked_lines("- 完全に消している\n", {1}, "完全に"), [(1, "- 完全に消している")])

    def test_HEADから変わっていない行は問わない(self):
        self.assertEqual(arw.asked_lines("- 前からある\n", set(), "- 前からある"), [])

    def test_空の行とコードブロックの中は問わない(self):
        text = "\n```\n- コード\n```\n"
        self.assertEqual(arw.asked_lines(text, None, text), [])

    def test_MultiEditの各編集で書いた文字列を集める(self):
        tool_input = {"edits": [{"new_string": "a"}, {"new_string": "b"}]}
        self.assertEqual(arw.written_text(tool_input).split(), ["a", "b"])


class 保存したときの動き(unittest.TestCase):
    """一時的な git リポジトリで、フックとして走らせたときの終了コードを見る。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for args in (["init", "-q"], ["config", "user.email", "t@example.com"],
                     ["config", "user.name", "t"]):
            subprocess.run(["git", *args], cwd=self.root, check=True)
        self.doc = self.root / "CLAUDE.md"
        self.doc.write_text("- 前からある\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=self.root, check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def run_hook(self, path, new_string):
        event = json.dumps({"tool_name": "Edit",
                            "tool_input": {"file_path": str(path), "new_string": new_string}})
        return subprocess.run([sys.executable, str(SCRIPT)], input=event.encode("utf-8"),
                              capture_output=True)

    def test_決まりの文書に行を足して保存すると問いが返る(self):
        self.doc.write_text("- 前からある\n- 足した\n", encoding="utf-8")
        r = self.run_hook(self.doc, "- 足した")
        self.assertEqual(r.returncode, 2)
        self.assertIn("CLAUDE.md:2", r.stderr.decode("utf-8"))

    def test_行を消しただけなら問わない(self):
        self.doc.write_text("", encoding="utf-8")
        self.assertEqual(self.run_hook(self.doc, "").returncode, 0)

    def test_決まりの文書でなければ問わない(self):
        other = self.root / "README.md"
        other.write_text("- 足した\n", encoding="utf-8")
        self.assertEqual(self.run_hook(other, "- 足した").returncode, 0)


if __name__ == "__main__":
    unittest.main()

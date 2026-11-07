"""claude/hooks/ask_removable_words.py が、この保存で足した行を並べて問い返すテスト。

仕様は docs/specs/ask_removable_words.py.md。
実行(この階層で): python -m unittest discover -s tests
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "claude" / "hooks" / "ask_removable_words.py"


class 保存したときの問い(unittest.TestCase):
    """一時的な git リポジトリで、フックとして走らせたときの終了コードと標準エラーを見る。"""

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

    def run_hook(self, tool_name, tool_input):
        event = json.dumps({"tool_name": tool_name,
                            "tool_input": {"file_path": str(self.doc), **tool_input}})
        r = subprocess.run([sys.executable, str(SCRIPT)], input=event.encode("utf-8"),
                           capture_output=True)
        return r.returncode, r.stderr.decode("utf-8")

    def edit(self, new_string):
        return self.run_hook("Edit", {"new_string": new_string})

    def test_この保存で書いた行だけを問う(self):
        self.doc.write_text("- 前からある\n- 足した\n- 別の保存で足した\n", encoding="utf-8")
        code, err = self.edit("- 足した")
        self.assertEqual(code, 2)
        self.assertIn("CLAUDE.md:2", err)
        self.assertNotIn("CLAUDE.md:3", err)

    def test_書いた文字列が行の一部でもその行を問う(self):
        self.doc.write_text("- 前からある\n- 完全に消している\n", encoding="utf-8")
        code, err = self.edit("完全に")
        self.assertEqual(code, 2)
        self.assertIn("CLAUDE.md:2", err)

    def test_HEADから変わっていない行は問わない(self):
        code, err = self.edit("- 前からある")
        self.assertEqual((code, err), (0, ""))

    def test_空の行とコードブロックの中は問わない(self):
        added = "\n```\n- コード\n```\n"
        self.doc.write_text("- 前からある\n" + added, encoding="utf-8")
        code, err = self.edit(added)
        self.assertEqual((code, err), (0, ""))

    def test_MultiEditの各編集とWriteのcontentを書いた文字列とする(self):
        self.doc.write_text("- 前からある\n- 一つ目\n- 二つ目\n", encoding="utf-8")
        code, err = self.run_hook("MultiEdit", {"edits": [{"new_string": "- 一つ目"},
                                                          {"new_string": "- 二つ目"}]})
        self.assertEqual(code, 2)
        self.assertIn("CLAUDE.md:2", err)
        self.assertIn("CLAUDE.md:3", err)
        self.doc.write_text("- 前からある\n- 書いた\n", encoding="utf-8")
        code, err = self.run_hook("Write", {"content": "- 前からある\n- 書いた\n"})
        self.assertEqual(code, 2)
        self.assertIn("CLAUDE.md:2", err)


if __name__ == "__main__":
    unittest.main()

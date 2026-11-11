"""claude/hooks/ask_about_written_lines.py が、この保存で足した行を並べて問い返すテスト。

仕様は docs/specs/ask_about_written_lines.py.md。
実行(この階層で): python -m unittest discover -s tests
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "claude" / "hooks" / "ask_about_written_lines.py"


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

    def test_知らせは消せる語と具体例や出来事の並びの2つを問う(self):
        self.doc.write_text("- 前からある\n- 足した\n", encoding="utf-8")
        code, err = self.edit("- 足した")
        self.assertEqual(code, 2)
        self.assertIn("1. 消しても意味が変わらない語は、消す。", err)
        self.assertIn("2. 言いたい決まりや事実を1文で言わずに、具体例や出来事を並べている所は", err)

    def test_自動メモリでもこの保存で書いた行だけを問う(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = Path(tmp) / "projects" / "p" / "memory" / "a.md"
            memory.parent.mkdir(parents=True)
            memory.write_text("- 前からある\n- 書いた\n- 別の保存で足した\n", encoding="utf-8")
            event = json.dumps({"tool_name": "Edit",
                                "tool_input": {"file_path": str(memory), "old_string": "",
                                               "new_string": "- 書いた"}})
            r = subprocess.run([sys.executable, str(SCRIPT)], input=event.encode("utf-8"),
                               capture_output=True, env={**os.environ, "CLAUDE_CONFIG_DIR": tmp})
            err = r.stderr.decode("utf-8")
            self.assertEqual(r.returncode, 2, err)
            self.assertIn("a.md:2", err)
            self.assertNotIn("a.md:1", err)
            self.assertNotIn("a.md:3", err)

    def test_自動メモリでないgitの外のファイルは問わない(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "projects" / "p" / "notes" / "a.md"
            doc.parent.mkdir(parents=True)
            doc.write_text("- 書いた\n", encoding="utf-8")
            event = json.dumps({"tool_name": "Edit",
                                "tool_input": {"file_path": str(doc), "new_string": "- 書いた"}})
            r = subprocess.run([sys.executable, str(SCRIPT)], input=event.encode("utf-8"),
                               capture_output=True, env={**os.environ, "CLAUDE_CONFIG_DIR": tmp})
            self.assertEqual((r.returncode, r.stderr), (0, b""))

    def test_段の見出しを足すとすぐ上の段から導いたかを問う(self):
        for heading in ("# 原則1: 安全", "## 目的: 足した目的", "### 目指す状態: 足した状態"):
            with self.subTest(heading=heading):
                self.doc.write_text(f"- 前からある\n{heading}\n", encoding="utf-8")
                code, err = self.edit(heading)
                self.assertEqual(code, 2)
                self.assertIn("3. 原則・目的・目指す状態の見出しは、すぐ上の段(原則なら命題)から導いた文にし", err)

    def test_段の見出しを足していなければ段の問いを出さない(self):
        self.doc.write_text("- 前からある\n- 足した\n", encoding="utf-8")
        code, err = self.edit("- 足した")
        self.assertEqual(code, 2)
        self.assertNotIn("すぐ上の段", err)

    def test_段の見出しに似た4段目の見出しでは段の問いを出さない(self):
        self.doc.write_text("- 前からある\n#### 目的\n", encoding="utf-8")
        code, err = self.edit("#### 目的")
        self.assertEqual(code, 2)
        self.assertNotIn("すぐ上の段", err)

    def test_段の問いの文はask_about_written_linesの1か所にだけある(self):
        sentence = "すぐ上の段(原則なら命題)から導いた文にし、下の段の手段の言葉を入れない。"
        found = [p.name for p in SCRIPT.parent.glob("*.py")
                 if sentence in p.read_text(encoding="utf-8")]
        self.assertEqual(found, ["ask_about_written_lines.py"])

    def test_問いの文はask_about_written_linesの1か所にだけある(self):
        sentence = "具体例や出来事を並べている所は、それらがみなそこから出てくる状態の1文に替える。"
        found = [p.name for p in SCRIPT.parent.glob("*.py")
                 if sentence in p.read_text(encoding="utf-8")]
        self.assertEqual(found, ["ask_about_written_lines.py"])


if __name__ == "__main__":
    unittest.main()

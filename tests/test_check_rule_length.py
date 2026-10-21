"""claude/hooks/check_rule_length.py が、新しく足した決まりの1行の字数を数えるテスト。

実行(この階層で): python -m unittest discover -s tests
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "claude" / "hooks" / "check_rule_length.py"
spec = importlib.util.spec_from_file_location("check_rule_length", SCRIPT)
crl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crl)

LONG = "- " + "あ" * 61
SHORT = "- " + "あ" * 60


class 決まりの1行の字数(unittest.TestCase):
    def test_上限を超えた新しい決まりの行を知らせる(self):
        self.assertEqual([n for n, _, _ in crl.too_long(f"# 見出し\n{LONG}\n{SHORT}\n", {2, 3})], [2])

    def test_前からある長い行は知らせない(self):
        self.assertEqual(crl.too_long(f"{LONG}\n{SHORT}\n", {2}), [])

    def test_コードは1字と数える(self):
        self.assertEqual(crl.rule_length("`python tools/check.py` を通している。"), 9)

    def test_コードブロックの中の箇条は数えない(self):
        self.assertEqual(crl.too_long(f"```\n{LONG}\n```\n", None), [])

    def test_一段下げた箇条も決まりの行として数える(self):
        self.assertEqual(len(crl.too_long("  " + LONG + "\n", None)), 1)

    def test_差分から足された行の番号を取り出す(self):
        diff = "@@ -10,0 +11,2 @@\n+- a\n+- b\n@@ -20 +22 @@\n-- old\n+- new\n"
        self.assertEqual(crl.added_line_numbers(diff), {11, 12, 22})

    def test_行を消しただけの差分は足された行にしない(self):
        self.assertEqual(crl.added_line_numbers("@@ -5,2 +4,0 @@\n-- a\n-- b\n"), set())


class 決まりの文書(unittest.TestCase):
    def test_CLAUDE_md_と_AGENTS_md_と_SKILL_md_は決まりの文書(self):
        for rel in ("CLAUDE.md", "sub/AGENTS.md", ".claude/skills/x/SKILL.md"):
            self.assertTrue(crl.is_rule_document(rel, []), rel)

    def test_リポジトリの一覧に書いた文書も決まりの文書(self):
        patterns = crl.read_patterns("# 説明\n\nrules/*.md\n")
        self.assertEqual(patterns, ["rules/*.md"])
        self.assertTrue(crl.is_rule_document("rules/a.md", patterns))
        self.assertFalse(crl.is_rule_document("README.md", patterns))


class 保存したときの動き(unittest.TestCase):
    """一時的な git リポジトリで、フックとして走らせたときの終了コードを見る。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for args in (["init", "-q"], ["config", "user.email", "t@example.com"],
                     ["config", "user.name", "t"]):
            subprocess.run(["git", *args], cwd=self.root, check=True)
        self.doc = self.root / "CLAUDE.md"
        self.doc.write_text(f"{LONG}\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=self.root, check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def run_hook(self, path):
        event = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(path)}})
        return subprocess.run([sys.executable, str(SCRIPT)], input=event.encode("utf-8"),
                              capture_output=True)

    def test_長い決まりを足して保存すると知らせが返る(self):
        self.doc.write_text(f"{LONG}\n{LONG}\n", encoding="utf-8")
        r = self.run_hook(self.doc)
        self.assertEqual(r.returncode, 2)
        self.assertIn("CLAUDE.md:2", r.stderr.decode("utf-8"))

    def test_前からある長い決まりだけなら知らせない(self):
        self.doc.write_text(f"{LONG}\n{SHORT}\n", encoding="utf-8")
        self.assertEqual(self.run_hook(self.doc).returncode, 0)

    def test_決まりの文書でなければ数えない(self):
        other = self.root / "README.md"
        other.write_text(f"{LONG}\n", encoding="utf-8")
        self.assertEqual(self.run_hook(other).returncode, 0)


if __name__ == "__main__":
    unittest.main()

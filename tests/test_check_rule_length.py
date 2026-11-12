"""claude/hooks/check_rule_length.py が、新しく足した決まりの1行の字数を数えるテスト。

仕様は docs/specs/check_rule_length.py.md。
実行(この階層で): python -m unittest discover -s tests
"""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "claude" / "hooks" / "check_rule_length.py"
spec = importlib.util.spec_from_file_location("check_rule_length", SCRIPT)
crl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crl)

LONG = "- " + "あ" * 61
SHORT = "- " + "あ" * 60


class 決まりの1行の字数(unittest.TestCase):
    def test_一段下げた箇条も決まりの行として数える(self):
        self.assertEqual(len(crl.too_long("  " + LONG + "\n", None)), 1)

    def test_コードブロックの中の箇条は数えない(self):
        self.assertEqual(crl.too_long(f"```\n{LONG}\n```\n", None), [])

    def test_60字までは知らせず61字から知らせる(self):
        self.assertEqual([n for n, _, _ in crl.too_long(f"# 見出し\n{LONG}\n{SHORT}\n", {2, 3})], [2])

    def test_リンクは文だけを数え60字までは知らせず61字から知らせる(self):
        self.assertEqual(crl.too_long("- [" + "あ" * 60 + "](x.md)\n", None), [])
        found = crl.too_long("- [" + "あ" * 61 + "](x.md)\n", None)
        self.assertEqual([length for _, length, _ in found], [61])

    def test_コードは1字と数える(self):
        self.assertEqual(crl.too_long("- " + "あ" * 59 + "`python x.py`\n", None), [])
        found = crl.too_long("- " + "あ" * 60 + "`python x.py`\n", None)
        self.assertEqual([length for _, length, _ in found], [61])


class プロンプト(unittest.TestCase):
    def test_CLAUDE_md_と_AGENTS_md_と_SKILL_md_はプロンプト(self):
        for rel in ("CLAUDE.md", "sub/AGENTS.md", ".claude/skills/x/SKILL.md"):
            self.assertTrue(crl.is_rule_document(rel, []), rel)

    def test_リポジトリの一覧に書いた文書もプロンプト(self):
        patterns = crl.read_patterns("# 説明\n\nrules/*.md\n")
        self.assertEqual(patterns, ["rules/*.md"])
        self.assertTrue(crl.is_rule_document("rules/a.md", patterns))
        self.assertFalse(crl.is_rule_document("README.md", patterns))


if __name__ == "__main__":
    unittest.main()

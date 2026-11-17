"""claude/hooks/rule_document_added_lines.py が、プロンプトを見分け、差分から足された行を取るテスト。

実行(この階層で): python -m unittest discover -s tests
"""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "claude" / "hooks" / "rule_document_added_lines.py"
spec = importlib.util.spec_from_file_location("rule_document_added_lines", SCRIPT)
rdl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rdl)


class プロンプト(unittest.TestCase):
    def test_CLAUDE_md_と_AGENTS_md_と_SKILL_md_はプロンプト(self):
        for rel in ("CLAUDE.md", "sub/AGENTS.md", ".claude/skills/x/SKILL.md"):
            self.assertTrue(rdl.is_rule_document(rel, []), rel)

    def test_リポジトリの一覧に書いた文書もプロンプト(self):
        patterns = rdl.read_patterns("# 説明\n\nrules/*.md\n")
        self.assertEqual(patterns, ["rules/*.md"])
        self.assertTrue(rdl.is_rule_document("rules/a.md", patterns))
        self.assertFalse(rdl.is_rule_document("README.md", patterns))


class 差分から足された行(unittest.TestCase):
    def test_差分で足された行の番号を取り消しただけの所は取らない(self):
        diff = "@@ -1,0 +2,2 @@\n+a\n+b\n@@ -5 +7 @@\n-x\n+y\n@@ -9,2 +10,0 @@\n-p\n-q\n"
        self.assertEqual(rdl.added_line_numbers(diff), {2, 3, 7})


if __name__ == "__main__":
    unittest.main()

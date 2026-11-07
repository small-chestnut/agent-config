"""claude/hooks/check_rule_length.py が、新しく足した決まりの1行の字数を数えるテスト。

仕様は docs/specs/check_rule_length.py.md。
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


def run_hook(path):
    event = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(path)}})
    return subprocess.run([sys.executable, str(SCRIPT)], input=event.encode("utf-8"),
                          capture_output=True)


def init_repo(root):
    for args in (["init", "-q"], ["config", "user.email", "t@example.com"],
                 ["config", "user.name", "t"]):
        subprocess.run(["git", *args], cwd=root, check=True)


class 保存したときの動き(unittest.TestCase):
    """一時的な git リポジトリで、フックとして走らせたときの終了コードを見る。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        init_repo(self.root)
        self.doc = self.root / "CLAUDE.md"
        self.doc.write_text(f"{LONG}\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=self.root, check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_足した長い決まりの行の番号をClaudeに返す(self):
        self.doc.write_text(f"{LONG}\n{LONG}\n", encoding="utf-8")
        r = run_hook(self.doc)
        self.assertEqual(r.returncode, 2)
        self.assertIn("CLAUDE.md:2", r.stderr.decode("utf-8"))

    def test_HEADからある長い決まりの行は知らせない(self):
        self.doc.write_text(f"{LONG}\n{SHORT}\n", encoding="utf-8")
        self.assertEqual(run_hook(self.doc).returncode, 0)

    def test_UTF_8でないプロンプトも落ちずに数える(self):
        self.doc.write_bytes(f"{LONG}\n{LONG}\n".encode("cp932"))
        r = run_hook(self.doc)
        self.assertEqual(r.returncode, 2, r.stderr.decode("utf-8", "replace"))


class gitの外と中にまだ無いファイル(unittest.TestCase):
    def test_gitにまだ入っていないプロンプトは全部の行を数える(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            doc = root / "CLAUDE.md"
            doc.write_text(f"{LONG}\n", encoding="utf-8")
            r = run_hook(doc)
            self.assertEqual(r.returncode, 2)
            self.assertIn("CLAUDE.md:1", r.stderr.decode("utf-8"))

    def test_gitの外のファイルは数えない(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "CLAUDE.md"
            doc.write_text(f"{LONG}\n", encoding="utf-8")
            self.assertEqual(run_hook(doc).returncode, 0)


class 決まりの1行の字数(unittest.TestCase):
    def test_一段下げた箇条も決まりの行として数える(self):
        self.assertEqual(len(crl.too_long("  " + LONG + "\n", None)), 1)

    def test_コードブロックの中の箇条は数えない(self):
        self.assertEqual(crl.too_long(f"```\n{LONG}\n```\n", None), [])

    def test_60字までは知らせず61字から知らせる(self):
        self.assertEqual([n for n, _, _ in crl.too_long(f"# 見出し\n{LONG}\n{SHORT}\n", {2, 3})], [2])

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

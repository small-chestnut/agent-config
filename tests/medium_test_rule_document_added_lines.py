"""claude/hooks/rule_document_added_lines.py が、保存されたプロンプトと自動メモリから、足された行を取るテスト。

一時ファイルと git を使うので medium。
実行(この階層で): python -m unittest discover -s tests -p "*test_*.py"
"""
import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "claude" / "hooks" / "rule_document_added_lines.py"
spec = importlib.util.spec_from_file_location("rule_document_added_lines", SCRIPT)
rdl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rdl)

OLD = "- 前からある行"
NEW = "- 足した行"
OTHER = "- もう1つの行"


def init_repo(root):
    for args in (["init", "-q"], ["config", "user.email", "t@example.com"],
                 ["config", "user.name", "t"]):
        subprocess.run(["git", *args], cwd=root, check=True)


class gitの中のプロンプト(unittest.TestCase):
    """一時的な git リポジトリで、コミットした後に書き換えたプロンプトを読む。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        init_repo(self.root)
        self.doc = self.root / "CLAUDE.md"
        self.doc.write_text(f"{OLD}\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=self.root, check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_HEADから足した行の番号だけを取る(self):
        self.doc.write_text(f"{OLD}\n{NEW}\n", encoding="utf-8", newline="\n")
        rel, text, new_lines = rdl.read_rule_document(self.doc)
        self.assertEqual((rel, text, new_lines), ("CLAUDE.md", f"{OLD}\n{NEW}\n", {2}))

    def test_UTF_8でないプロンプトも落ちずに読む(self):
        self.doc.write_bytes(f"{OLD}\n{NEW}\n".encode("cp932"))
        doc = rdl.read_rule_document(self.doc)
        self.assertEqual(doc[0], "CLAUDE.md")

    def test_プロンプトでないファイルは取らない(self):
        readme = self.root / "README.md"
        readme.write_text(f"{NEW}\n", encoding="utf-8")
        self.assertIsNone(rdl.read_rule_document(readme))


class gitの外と中にまだ無いファイル(unittest.TestCase):
    def test_gitにまだ入っていないプロンプトは全部の行を足された行とする(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            doc = root / "CLAUDE.md"
            doc.write_text(f"{NEW}\n", encoding="utf-8")
            rel, _, new_lines = rdl.read_rule_document(doc)
            self.assertEqual((rel, new_lines), ("CLAUDE.md", None))

    def test_gitの外のファイルは取らない(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "CLAUDE.md"
            doc.write_text(f"{NEW}\n", encoding="utf-8")
            self.assertIsNone(rdl.read_rule_document(doc))


class 自動メモリ(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.config = Path(self.tmp.name)
        self.memory = self.config / "projects" / "p" / "memory" / "a.md"
        self.memory.parent.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def config_dir(self, path):
        return mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": str(path)})

    def test_自動メモリはこの保存で書いた行だけを足された行とする(self):
        self.memory.write_text(f"{OLD}\n{NEW}\n", encoding="utf-8", newline="\n")
        with self.config_dir(self.config):
            rel, _, new_lines = rdl.read_rule_document(self.memory, {"old_string": "", "new_string": NEW})
        self.assertEqual((rel, new_lines), (self.memory.as_posix(), {2}))

    def test_設定ディレクトリの外のmemoryフォルダのmdは自動メモリでない(self):
        other = self.config / "other" / "projects" / "p" / "memory" / "a.md"
        config = self.config / "cfg"
        notes = config / "projects" / "p" / "notes" / "a.md"
        with self.config_dir(config):
            self.assertFalse(rdl.is_memory(other))
            self.assertFalse(rdl.is_memory(notes))
            self.assertTrue(rdl.is_memory(config / "projects" / "p" / "memory" / "a.md"))

    def test_CLAUDE_CONFIG_DIRが無ければホームの_claudeの下を自動メモリとする(self):
        memory = self.config / ".claude" / "projects" / "p" / "memory" / "a.md"
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CONFIG_DIR"}
        env.update(HOME=str(self.config), USERPROFILE=str(self.config))
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertTrue(rdl.is_memory(memory))

    def test_自動メモリのEditでold_stringから写した変わらない行は足された行としない(self):
        text = f"{OLD}\n{NEW}\n{OTHER}\n"
        added = rdl.memory_added_lines(text, {"old_string": OLD, "new_string": f"{OLD}\n{NEW}\n{OTHER}"})
        self.assertEqual(added, {2, 3})

    def test_自動メモリで書いた行を含むだけのほかの行は足された行としない(self):
        text = "- 短い行 の続き\n- 古い\n- 短い行\n"
        added = rdl.memory_added_lines(text, {"old_string": "- 古い", "new_string": "- 短い行"})
        self.assertEqual(added, {3})

    def test_自動メモリのEditで書いた所が1つに決まらなければ現れる所をみな足された行とする(self):
        # 行の境目に当たる所が無い(行の一部)
        text = "- 長い行の規則です\n- 短い行の規則\n"
        added = rdl.memory_added_lines(text, {"old_string": "foo", "new_string": "の規則"})
        self.assertEqual(added, {1, 2})
        # 行の境目に当たる所が2つ以上ある
        text = "- 同じ行\n- 同じ行\n- 同じ行です\n"
        added = rdl.memory_added_lines(text, {"old_string": "x", "new_string": "- 同じ行"})
        self.assertEqual(added, {1, 2, 3})

    def test_自動メモリをWriteで書くと全部の行を足された行とする(self):
        self.assertIsNone(rdl.memory_added_lines(f"{NEW}\n", {"content": f"{NEW}\n"}))


if __name__ == "__main__":
    unittest.main()

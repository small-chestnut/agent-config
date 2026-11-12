"""claude/hooks/check_rule_length.py が、新しく足した決まりの1行の字数を数えるテスト。

仕様は docs/specs/check_rule_length.py.md。
一時ファイル・git・ほかのプロセスを使うので中。
実行(この階層で): python -m unittest discover -s tests -p "*test_*.py"
"""
import importlib.util
import json
import os
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


def run_memory_hook(config_dir, path, tool_name, tool_input, env=None):
    """自動メモリを保存したときのフックを、CLAUDE_CONFIG_DIR を指定して走らせる。env を渡すと、それだけの環境変数。"""
    event = json.dumps({"tool_name": tool_name, "tool_input": {"file_path": str(path), **tool_input}})
    if env is None:
        env = {**os.environ, "CLAUDE_CONFIG_DIR": str(config_dir)}
    return subprocess.run([sys.executable, str(SCRIPT)], input=event.encode("utf-8"),
                          capture_output=True, env=env)


class 自動メモリ(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.config = Path(self.tmp.name)
        self.memory = self.config / "projects" / "p" / "memory" / "a.md"
        self.memory.parent.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_自動メモリに足した長い決まりの行の番号をClaudeに返す(self):
        self.memory.write_text(f"{SHORT}\n{LONG}\n", encoding="utf-8")
        r = run_memory_hook(self.config, self.memory, "Edit", {"old_string": "", "new_string": LONG})
        self.assertEqual(r.returncode, 2, r.stderr.decode("utf-8"))
        self.assertIn("a.md:2", r.stderr.decode("utf-8"))

    def test_自動メモリのこの保存で書いていない長い行は知らせない(self):
        self.memory.write_text(f"{LONG}\n{SHORT}\n", encoding="utf-8")
        r = run_memory_hook(self.config, self.memory, "Edit", {"old_string": "", "new_string": SHORT})
        self.assertEqual((r.returncode, r.stderr), (0, b""))

    def test_設定ディレクトリの外のmemoryフォルダのmdは数えない(self):
        other = self.config / "other" / "projects" / "p" / "memory" / "a.md"
        other.parent.mkdir(parents=True)
        other.write_text(f"{LONG}\n", encoding="utf-8")
        config = self.config / "cfg"
        config.mkdir()
        r = run_memory_hook(config, other, "Edit", {"new_string": LONG})
        self.assertEqual((r.returncode, r.stderr), (0, b""))
        notes = config / "projects" / "p" / "notes" / "a.md"
        notes.parent.mkdir(parents=True)
        notes.write_text(f"{LONG}\n", encoding="utf-8")
        r = run_memory_hook(config, notes, "Edit", {"new_string": LONG})
        self.assertEqual((r.returncode, r.stderr), (0, b""))

    def test_CLAUDE_CONFIG_DIRが無ければホームの_claudeの自動メモリを数える(self):
        memory = self.config / ".claude" / "projects" / "p" / "memory" / "a.md"
        memory.parent.mkdir(parents=True)
        memory.write_text(f"{LONG}\n", encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CONFIG_DIR"}
        env.update(HOME=str(self.config), USERPROFILE=str(self.config))
        r = run_memory_hook(None, memory, "Write", {"content": f"{LONG}\n"}, env=env)
        self.assertEqual(r.returncode, 2, r.stderr.decode("utf-8"))
        self.assertIn("a.md:1", r.stderr.decode("utf-8"))

    def test_自動メモリのEditでold_stringから写した変わらない行は知らせない(self):
        text = f"{LONG}\n{SHORT}\n- {'い' * 61}\n"
        added = crl.memory_added_lines(text, {"old_string": LONG, "new_string": f"{LONG}\n{SHORT}\n- {'い' * 61}"})
        self.assertEqual(added, {2, 3})

    def test_自動メモリで書いた行を含むだけのほかの行は知らせない(self):
        text = f"- 短い行 {'あ' * 60}\n- 古い\n- 短い行\n"
        added = crl.memory_added_lines(text, {"old_string": "- 古い", "new_string": "- 短い行"})
        self.assertEqual(added, {3})

    def test_自動メモリのEditで書いた所が1つに決まらなければ現れる所をみな数える(self):
        # 行の境目に当たる所が無い(行の一部)
        text = f"- {'あ' * 55}の規則です\n- 短い行の規則\n"
        added = crl.memory_added_lines(text, {"old_string": "foo", "new_string": "の規則"})
        self.assertEqual(added, {1, 2})
        # 行の境目に当たる所が2つ以上ある
        text = "- 同じ行\n- 同じ行\n- 同じ行です\n"
        added = crl.memory_added_lines(text, {"old_string": "x", "new_string": "- 同じ行"})
        self.assertEqual(added, {1, 2, 3})

    def test_自動メモリをWriteで書くと全部の行を数える(self):
        self.assertIsNone(crl.memory_added_lines(f"{LONG}\n", {"content": f"{LONG}\n"}))
        self.memory.write_text(f"{LONG}\n{LONG}\n", encoding="utf-8")
        r = run_memory_hook(self.config, self.memory, "Write", {"content": f"{LONG}\n{LONG}\n"})
        err = r.stderr.decode("utf-8")
        self.assertEqual(r.returncode, 2, err)
        self.assertIn("a.md:1", err)
        self.assertIn("a.md:2", err)


if __name__ == "__main__":
    unittest.main()

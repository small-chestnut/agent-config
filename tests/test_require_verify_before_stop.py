"""claude/hooks/require_verify_before_stop.py が、中身が変わったのに確かめが通っていないターンを止めるテスト。

実行(この階層で): python -m unittest discover -s tests
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "claude" / "hooks"
SCRIPT = HOOKS / "require_verify_before_stop.py"
spec = importlib.util.spec_from_file_location("require_verify_before_stop", SCRIPT)
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class 確かめのコマンドの一覧(unittest.TestCase):
    def test_確かめのコマンドの一覧は空の行と井桁の行を読まない(self):
        text = "# 説明\n\npython -m unittest\n  npm test  \n"
        self.assertEqual(verify.read_commands(text), ["python -m unittest", "npm test"])


class 確かめとして数えるコマンド(unittest.TestCase):
    HEADS = ["python -m unittest", "npm test"]

    def count(self, command, background=False):
        return verify.counted_heads(command, background, self.HEADS)

    def test_頭と同じか頭と空白で始まるコマンドを確かめとして数える(self):
        self.assertEqual(self.count("python -m unittest"), ["python -m unittest"])
        self.assertEqual(self.count("  python -m unittest discover -s tests "), ["python -m unittest"])

    def test_頭の直後が空白でなければ数えない(self):
        self.assertEqual(self.count("python -m unittests"), [])
        self.assertEqual(self.count("npm testing"), [])

    def test_パイプとセミコロンとアンドと改行を含むコマンドは数えない(self):
        for c in ("npm test | tail", "npm test; echo", "npm test && echo", "npm test &", "npm test\necho"):
            self.assertEqual(self.count(c), [], c)

    def test_標準エラーを標準出力へ向けたコマンドは数える(self):
        self.assertEqual(self.count("npm test 2>&1"), ["npm test"])

    def test_バックグラウンドで走らせたコマンドは数えない(self):
        self.assertEqual(self.count("npm test", background=True), [])


class 止めるかどうか(unittest.TestCase):
    HEADS = ["a", "b"]

    def test_ターンの始めの印が無ければ止めない(self):
        self.assertEqual(verify.unpassed_heads(None, "now", {}, self.HEADS), [])

    def test_ターンの始めから中身が変わっていなければ止めない(self):
        self.assertEqual(verify.unpassed_heads("same", "same", {}, self.HEADS), [])

    def test_今の中身で通っていない確かめの頭を返す(self):
        self.assertEqual(verify.unpassed_heads("old", "now", {"now": ["a"], "old": ["b"]}, self.HEADS), ["b"])

    def test_今の中身で全部の確かめが通っていれば止めない(self):
        self.assertEqual(verify.unpassed_heads("old", "now", {"now": ["b", "a"]}, self.HEADS), [])


class 確かめの記録のロック(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "claude-verify.json"
        self.lock = Path(self.tmp.name) / "claude-verify.json.lock"

    def put(self, r):
        r["turn_start"]["s"] = "x"

    def make_lock(self, age):
        self.lock.write_text("")
        t = time.time() - age
        os.utime(self.lock, (t, t))

    def test_30秒より古いロックは消して記録を書く(self):
        self.make_lock(31)
        self.assertTrue(verify.update_record(self.path, self.put, wait=0.2))
        self.assertEqual(verify.load_record(self.path)["turn_start"], {"s": "x"})
        self.assertFalse(self.lock.exists())

    def test_30秒に満たないロックが待ち時間を過ぎても残れば書かずに戻る(self):
        self.make_lock(29)
        self.assertFalse(verify.update_record(self.path, self.put, wait=0.2))
        self.assertFalse(self.path.exists())
        self.assertTrue(self.lock.exists())

    def test_確かめの記録が読めないか壊れていれば空として扱う(self):
        empty = {"turn_start": {}, "passed": {}}
        self.assertEqual(verify.load_record(self.path), empty)
        self.path.write_text("{壊れ", encoding="utf-8")
        self.assertEqual(verify.load_record(self.path), empty)
        self.path.write_text("[1]", encoding="utf-8")
        self.assertEqual(verify.load_record(self.path), empty)
        self.assertTrue(verify.update_record(self.path, self.put))
        self.assertEqual(verify.load_record(self.path)["turn_start"], {"s": "x"})


class フックを走らせる(unittest.TestCase):
    """一時的な git リポジトリで、フックを subprocess で走らせる。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name).resolve() / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        (self.repo / "a.txt").write_text("1")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "first")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True, text=True, check=True).stdout.strip()

    def write_list(self, *heads):
        (self.repo / ".claude").mkdir(exist_ok=True)
        (self.repo / ".claude" / "verify-commands.txt").write_text("\n".join(heads) + "\n", encoding="utf-8")

    def run_hook(self, mode, payload=None, cwd=None):
        data = {"session_id": "s1", "cwd": str(cwd or self.repo), **(payload or {})}
        return subprocess.run(
            [sys.executable, str(SCRIPT), mode], input=json.dumps(data), capture_output=True, text=True,
            encoding="utf-8", cwd=cwd or self.repo,
        )

    def sig(self):
        return verify.content_sig(str(self.repo))

    def test_コミットしても中身の印は変わらない(self):
        (self.repo / "a.txt").write_text("2")
        before = self.sig()
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "second")
        self.assertEqual(self.sig(), before)

    def test_docsの下だけを変えても中身の印は変わらない(self):
        before = self.sig()
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / "n.md").write_text("x")
        self.assertEqual(self.sig(), before)

    def test_まだ追っていないファイルを足すと中身の印が変わる(self):
        before = self.sig()
        (self.repo / "new.txt").write_text("x")
        self.assertNotEqual(self.sig(), before)

    def test_確かめを通すまでStopフックが止め通したら止めない(self):
        self.write_list("python -m unittest")
        self.run_hook("turn-start")
        (self.repo / "a.txt").write_text("2")
        r = self.run_hook("stop")
        self.assertEqual(r.returncode, 2)
        self.assertIn("python -m unittest", r.stderr)
        ok = {"tool_input": {"command": "python -m unittest discover -s tests"}}
        self.assertEqual(self.run_hook("record", ok).returncode, 0)
        self.assertEqual(self.run_hook("stop").returncode, 0)
        (self.repo / "a.txt").write_text("3")
        self.assertEqual(self.run_hook("stop").returncode, 2)

    def test_一覧の無いリポジトリではフックが何もしない(self):
        self.run_hook("turn-start")
        (self.repo / "a.txt").write_text("2")
        self.assertEqual(self.run_hook("stop").returncode, 0)

    def test_gitの外ではフックが何もしない(self):
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        for mode in ("turn-start", "record", "stop"):
            r = self.run_hook(mode, cwd=outside)
            self.assertEqual((r.returncode, r.stderr), (0, ""))

    def test_同時に記録しても通った頭が消えない(self):
        heads = [f"check{i}" for i in range(8)]
        self.write_list(*heads)
        self.run_hook("turn-start")
        (self.repo / "a.txt").write_text("2")
        procs = []
        for h in heads:
            data = {"session_id": "s1", "cwd": str(self.repo), "tool_input": {"command": h}}
            p = subprocess.Popen([sys.executable, str(SCRIPT), "record"], stdin=subprocess.PIPE,
                                 text=True, encoding="utf-8", cwd=self.repo)
            p.stdin.write(json.dumps(data))
            p.stdin.close()
            procs.append(p)
        for p in procs:
            p.wait()
        self.assertEqual(self.run_hook("stop").returncode, 0)


if __name__ == "__main__":
    unittest.main()

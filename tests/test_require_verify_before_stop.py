"""claude/hooks/require_verify_before_stop.py が、作業ツリーが変わったのに検証コマンドが通っていないターンを止めるテスト。

実行(この階層で): python -m unittest discover -s tests
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "claude" / "hooks"
SCRIPT = HOOKS / "require_verify_before_stop.py"
spec = importlib.util.spec_from_file_location("require_verify_before_stop", SCRIPT)
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class 検証コマンドの一覧(unittest.TestCase):
    def test_検証コマンドの一覧は空行とコメント行を読まない(self):
        text = "# 説明\n\npython -m unittest\n  npm test  \n"
        self.assertEqual(verify.read_commands(text), ["python -m unittest", "npm test"])


class 検証として数えるコマンド(unittest.TestCase):
    HEADS = ["python -m unittest", "npm test"]

    def count(self, command, background=False):
        return verify.counted_heads(command, background, self.HEADS)

    def test_プレフィックスと同じかプレフィックスと空白で始まるコマンドを検証として数える(self):
        self.assertEqual(self.count("python -m unittest"), ["python -m unittest"])
        self.assertEqual(self.count("  python -m unittest discover -s tests "), ["python -m unittest"])

    def test_プレフィックスの直後が空白でなければ数えない(self):
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

    def test_ターン開始時の作業ツリーのハッシュ値が無ければ止めない(self):
        self.assertEqual(verify.unpassed_heads(None, "now", {}, self.HEADS), [])

    def test_ターン開始時から作業ツリーが変わっていなければ止めない(self):
        self.assertEqual(verify.unpassed_heads("same", "same", {}, self.HEADS), [])

    def test_今の作業ツリーで通っていない検証コマンドを返す(self):
        self.assertEqual(verify.unpassed_heads("old", "now", {"now": ["a"], "old": ["b"]}, self.HEADS), ["b"])

    def test_今の作業ツリーで全部の検証コマンドが通っていれば止めない(self):
        self.assertEqual(verify.unpassed_heads("old", "now", {"now": ["b", "a"]}, self.HEADS), [])


class 検証の状態ファイルの件数(unittest.TestCase):
    def test_書き直したターン開始時の作業ツリーのハッシュ値は新しいものとして残す(self):
        record = {"turn_start": {}, "passed": {}}
        verify.put_latest(record["turn_start"], "long", "1")
        for i in range(verify.KEEP):
            verify.put_latest(record["turn_start"], f"s{i}", "x")
        verify.put_latest(record["turn_start"], "long", "2")
        verify.trim(record)
        self.assertEqual(record["turn_start"]["long"], "2")


if __name__ == "__main__":
    unittest.main()

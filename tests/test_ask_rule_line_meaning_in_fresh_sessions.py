"""claude/skills/prompt-structure/ask_rule_line_meaning_in_fresh_sessions.py が、規則の1行を決まりの文書を読まない3つのセッションに読ませるテスト。

仕様は docs/specs/ask_rule_line_meaning_in_fresh_sessions.py.md。
実行(この階層で): python -m unittest discover -s tests
"""
import contextlib
import importlib.util
import io
import os
import subprocess
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "claude" / "skills" / "prompt-structure" / "ask_rule_line_meaning_in_fresh_sessions.py"
)
spec = importlib.util.spec_from_file_location("ask_rule_line_meaning_in_fresh_sessions", SCRIPT)
ask = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ask)

RULE = "- 返答は、結論から書いている。"
CLAUDE = "/fake/bin/claude"


class 記録するセッション:
    """run_session の代わり。呼ばれた引数・フォルダ・環境変数を記録し、決めた答えを返す。"""

    def __init__(self, results=None):
        self.calls = []
        self.results = results

    def __call__(self, args, cwd, env, input_text):
        self.calls.append({
            "args": list(args), "cwd": cwd, "env": dict(env), "input_text": input_text,
            "cwd_existed": os.path.isdir(cwd),
        })
        if self.results is not None:
            return self.results[len(self.calls) - 1]
        return 0, f"答え本文{len(self.calls)}"


def run_main(argv, session, find_claude=lambda name: CLAUDE):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = ask.main(argv, run_session=session, find_claude=find_claude)
    return code, out.getvalue()


def option_value(args, name):
    return args[args.index(name) + 1]


class 規則の1行を3つのセッションに読ませる(unittest.TestCase):
    def test_規則の1行を3つのセッションに読ませて3つの答えを番号の見出しの下に並べる(self):
        session = 記録するセッション([(0, "一つ目の答え"), (0, "二つ目の答え"), (0, "三つ目の答え")])
        code, out = run_main([RULE], session)
        self.assertEqual(code, 0)
        self.assertEqual(len(session.calls), 3)
        positions = [out.index(f"## 答え{n}") for n in (1, 2, 3)]
        self.assertEqual(positions, sorted(positions))
        for n, text in enumerate(["一つ目の答え", "二つ目の答え", "三つ目の答え"], start=1):
            heading = out.index(f"## 答え{n}")
            self.assertEqual(out[heading:].split("\n", 1)[1].split("## 答え")[0].strip(), text)

    def test_セッションごとに別の新しい空のフォルダから起動する(self):
        session = 記録するセッション()
        run_main([RULE], session)
        cwds = [c["cwd"] for c in session.calls]
        self.assertEqual(len(set(cwds)), 3)
        self.assertTrue(all(c["cwd_existed"] for c in session.calls))
        self.assertEqual(session.calls[0]["args"][:2], [CLAUDE, "-p"])

    def test_CLAUDE_mdを読まない環境変数を付けて起動しHOMEとUSERPROFILEは変えない(self):
        session = 記録するセッション()
        with mock.patch.dict(os.environ, {"HOME": "/home/tester", "USERPROFILE": "C:/Users/tester"}):
            run_main([RULE], session)
        for call in session.calls:
            self.assertEqual(call["env"]["CLAUDE_CODE_DISABLE_CLAUDE_MDS"], "1")
            self.assertEqual(call["env"]["HOME"], "/home/tester")
            self.assertEqual(call["env"]["USERPROFILE"], "C:/Users/tester")

    def test_設定とskillと道具を使わず記録を残さない指定で起動する(self):
        session = 記録するセッション()
        run_main([RULE], session)
        for call in session.calls:
            args = call["args"]
            self.assertEqual(option_value(args, "--setting-sources"), "")
            self.assertIn("--disable-slash-commands", args)
            self.assertEqual(option_value(args, "--tools"), "")
            self.assertIn("--no-session-persistence", args)

    def test_読ませる文は引数でなく標準入力で渡す(self):
        session = 記録するセッション()
        run_main([RULE], session)
        for call in session.calls:
            self.assertTrue(call["input_text"].endswith(RULE))
            self.assertNotIn(RULE, " ".join(call["args"]))
            self.assertNotIn("1. 何をする決まりか", " ".join(call["args"]))
        text = "読ませる文\n& 100%"
        completed = subprocess.CompletedProcess(["claude"], 0, stdout="答え", stderr="")
        with mock.patch.object(ask.subprocess, "run", return_value=completed) as run:
            code, output = ask.run_session([CLAUDE, "-p"], "/tmp/empty", {"A": "1"}, text)
        self.assertEqual((code, output), (0, "答え"))
        self.assertEqual(run.call_args.kwargs["input"], text)
        self.assertEqual(run.call_args.kwargs["encoding"], "utf-8")
        self.assertNotIn("stdin", run.call_args.kwargs)
        self.assertEqual(run.call_args.kwargs["cwd"], "/tmp/empty")

    def test_読ませる文は4つの問いと規則の1行だけ(self):
        session = 記録するセッション()
        run_main([RULE], session)
        prompt = session.calls[0]["input_text"]
        self.assertEqual(prompt, ask.QUESTION + "\n\n" + RULE)
        for question in ("1. 何をする決まりか", "2. 守っている例", "3. 破っている例", "4. 意味が1つに決まらない所"):
            self.assertIn(question, prompt)
        self.assertTrue(prompt.endswith(RULE))

    def test_モデルを指定しなければOpusで起動する(self):
        session = 記録するセッション()
        run_main([RULE], session)
        for call in session.calls:
            self.assertEqual(option_value(call["args"], "--model"), "claude-opus-5-5")

    def test_指定したモデルで起動する(self):
        session = 記録するセッション()
        run_main([RULE, "--model", "claude-sonnet-5-5"], session)
        for call in session.calls:
            self.assertEqual(option_value(call["args"], "--model"), "claude-sonnet-5-5")

    def test_1つでも失敗したセッションがあれば出力を添えて終了コード1で終わる(self):
        session = 記録するセッション([(0, "答え1"), (3, "認証エラーの出力"), (0, "答え3")])
        code, out = run_main([RULE], session)
        self.assertEqual(code, 1)
        self.assertIn("認証エラーの出力", out)

    def test_claudeのコマンドが見つからなければ終了コード1で終わる(self):
        session = 記録するセッション()
        code, out = run_main([RULE], session, find_claude=lambda name: None)
        self.assertEqual(code, 1)
        self.assertIn("claude", out)
        self.assertEqual(session.calls, [])

    def test_作った空のフォルダは終わったら消す(self):
        session = 記録するセッション()
        run_main([RULE], session)
        for call in session.calls:
            self.assertFalse(os.path.exists(call["cwd"]))


if __name__ == "__main__":
    unittest.main()

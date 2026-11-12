"""claude/hooks/remind_pin_after_starting_se.py が、SE を起こした後にピン留めを知らせるテスト。

仕様は docs/specs/remind_pin_after_starting_se.py.md。
入力の JSON を関数に渡すだけなので、1つのプロセスのメモリだけで終わる小。
実行(この階層で): python -m unittest discover -s tests
"""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "claude" / "hooks" / "remind_pin_after_starting_se.py"
spec = importlib.util.spec_from_file_location("remind_pin_after_starting_se", SCRIPT)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

START = "mcp__ccd_session__start_session"


class SEのピン留めを知らせる(unittest.TestCase):
    def test_nameがseで終わるセッションを起こした後にピン留めを知らせる(self):
        message = hook.pin_message({"tool_name": START, "tool_input": {"name": "0071-se"}})
        self.assertEqual(message, "起こした SE を、`set_pinned` でピン留めする。(ADR 0057-2)")

    def test_nameがseで終わらないセッションの後には知らせない(self):
        for name in ("0071-pg", "0071-sea"):
            with self.subTest(name=name):
                self.assertIsNone(hook.pin_message({"tool_name": START, "tool_input": {"name": name}}))

    def test_nameの無いstart_sessionの後には知らせない(self):
        self.assertIsNone(hook.pin_message({"tool_name": START, "tool_input": {"title": "x"}}))


if __name__ == "__main__":
    unittest.main()

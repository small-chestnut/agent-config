"""全体の CLAUDE.md(claude/CLAUDE.md)の字数が、上限以内であることを確かめるテスト。

字数は、改行も1字と数える(read_text が CRLF を LF にして読む)。
リポジトリのファイルを使うので中。
実行(この階層で): python -m unittest tests/medium_test_global_claude_md_length.py
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOBAL_CLAUDE_MD = ROOT / "claude" / "CLAUDE.md"
LIMIT = 8000


class 全体のCLAUDE_mdの字数(unittest.TestCase):
    """毎回読まれる量を、行の数でなく字の数で止める。(ADR 0076-1)"""

    def test_全体のCLAUDE_mdは8000字以内(self):
        count = len(GLOBAL_CLAUDE_MD.read_text(encoding="utf-8"))
        if count > LIMIT:
            self.fail(
                f"claude/CLAUDE.md は {count} 字で、上限 {LIMIT} 字を超えています。"
                ".claude/rules/global-claude-md.md の"
                "「上限を超えるときも、毎回読まれる量を増やさずに収めている」"
                "のとおりに減らしてください。"
            )


if __name__ == "__main__":
    unittest.main()

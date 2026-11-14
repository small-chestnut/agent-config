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
                f"claude/CLAUDE.md は {count} 字で、上限 {LIMIT} 字を超えています(ADR 0076-1)。"
                "次の順に減らしてください(ADR 0076-2)。"
                "1. 減らすのは、安全の原則の節(800 字前後)のほかの行。"
                "2. まず、振る舞いを変えていない行を消す。"
                "3. 次に、特定の作業でだけ要る行を、その作業の skill に移す。"
                "4. 字数は、行ごと消すか移して減らす。"
                "5. それでも収まらなければ、足す行と消す候補の行の目的を並べ、"
                "どちらを先にするかを利用者に聞く。"
            )


if __name__ == "__main__":
    unittest.main()

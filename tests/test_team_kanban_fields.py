"""skill team-kanban が書くカードの項目が、かんばんのページの読む項目と同じことを確かめるテスト。

実行(この階層で): python -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "claude" / "skills" / "team-kanban" / "SKILL.md"
PAGE = ROOT / ".claude" / "skills" / "team-kanban-page" / "index.html"


class かんばんのカードの項目(unittest.TestCase):
    def test_手順が書く項目は_ページが読む項目と同じ(self):
        lines = SKILL.read_text(encoding="utf-8").splitlines()
        line = next(l for l in lines if l.startswith("- 1行の項目は、"))
        written = set(re.findall(r"`(\w+)`", line))

        page = PAGE.read_text(encoding="utf-8")
        loader = page[page.index("dash.loader('cards'"):page.index("dash.onData(")]
        read = set(re.findall(r"\br\.(\w+)", loader))

        self.assertTrue(written)
        self.assertEqual(written, read)


if __name__ == "__main__":
    unittest.main()

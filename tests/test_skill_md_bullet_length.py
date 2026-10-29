"""claude/skills/*/SKILL.md の箇条書きの行が、すべて上限の字数以内であることを確かめるテスト。

字数の数え方は claude/hooks/check_rule_length.py のものをそのまま使う。
実行(この階層で): python -m unittest discover -s tests
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "claude" / "hooks" / "check_rule_length.py"
spec = importlib.util.spec_from_file_location("check_rule_length", SCRIPT)
crl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crl)

SKILL_MDS = sorted((ROOT / "claude" / "skills").glob("*/SKILL.md"))


class SKILL_mdの箇条書きの字数(unittest.TestCase):
    def test_どのSKILL_mdの箇条書きの行も60字以内(self):
        for path in SKILL_MDS:
            with self.subTest(file=path.relative_to(ROOT).as_posix()):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(crl.too_long(text, None), [])

    def test_確かめるSKILL_mdが1つ以上見つかる(self):
        self.assertTrue(SKILL_MDS)


if __name__ == "__main__":
    unittest.main()

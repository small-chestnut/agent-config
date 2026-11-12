"""claude/hooks/check_rule_documents_changed_by_shell.py が、シェルで書き換えたプロンプトを数え、問い返すテスト。

実行(この階層で): python -m unittest discover -s tests
"""
import importlib.util
import sys
import unittest
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "claude" / "hooks"
SCRIPT = HOOKS / "check_rule_documents_changed_by_shell.py"
sys.path.insert(0, str(HOOKS))
spec = importlib.util.spec_from_file_location("check_rule_documents_changed_by_shell", SCRIPT)
shell = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shell)


class 取り込むgitコマンド(unittest.TestCase):
    def test_取り込むgitコマンドを見分ける(self):
        for command in ("git merge --ff-only origin/main", "git -C x pull", "cd a && git checkout main",
                        "git cherry-pick abc"):
            self.assertTrue(shell.brings_other_commits(command), command)

    def test_取り込まないコマンドは見分けない(self):
        for command in ("git commit -am x", "git add .", "git stash pop", "git log --grep merge",
                        "git merge-base a b", "python edit.py"):
            self.assertFalse(shell.brings_other_commits(command), command)


class 取り込んだ行(unittest.TestCase):
    def test_コンフリクトマーカーの行は取り込んだ行に数える(self):
        text = "<<<<<<< HEAD\n- a\n=======\n- b\n>>>>>>> other\n"
        self.assertEqual(shell.imported_lines(text, []), {1, 3, 5})

    def test_コンフリクトマーカーに似た行は取り込んだ行に数えない(self):
        text = "========\n- =======\n<<<<<<<x\n"
        self.assertEqual(shell.imported_lines(text, []), set())

    def test_どれかの版と同じ行は取り込んだ行に数える(self):
        self.assertEqual(shell.imported_lines("- a\n- b\n- c\n", ["- a\n- c\n", "- b\n"]), {1, 2, 3})
        self.assertEqual(shell.imported_lines("- a\n- b\n- c\n", ["- a\n"]), {1})


if __name__ == "__main__":
    unittest.main()

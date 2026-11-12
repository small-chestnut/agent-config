"""claude/hooks/add_messaging_skill_to_team_roles.py が、役割の skill の後に task-team-messaging を渡すテスト。

仕様は docs/specs/add_messaging_skill_to_team_roles.py.md。
一時フォルダに SKILL.md を置いて読む。一時ファイルを使うので中。
実行(この階層で): python -m unittest discover -s tests -p "*test_*.py"
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "claude" / "hooks" / "add_messaging_skill_to_team_roles.py"
spec = importlib.util.spec_from_file_location("add_messaging_skill_to_team_roles", SCRIPT)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

SKILL = "---\nname: task-team-messaging\ndescription: 知らせる規則。\n---\n\n# 原則1\n\n- 行1\n"


def event(skill):
    return {"tool_name": "Skill", "tool_input": {"skill": skill}}


class メッセージの規則を渡す(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.skills = Path(self.dir.name)

    def put_skill(self, text=SKILL):
        folder = self.skills / "task-team-messaging"
        folder.mkdir()
        (folder / "SKILL.md").write_text(text, encoding="utf-8")

    def test_SEとPGとQAのskillを読んだ後にtask_team_messagingの本文を渡す(self):
        self.put_skill()
        for skill in ("task-team-se", "task-team-pg", "task-team-qa"):
            with self.subTest(skill=skill):
                message = hook.messaging_message(event(skill), self.skills)
                self.assertEqual(message, "skill `task-team-messaging` も読む。\n# 原則1\n\n- 行1")

    def test_ほかのskillを読んだ後には何も渡さない(self):
        self.put_skill()
        for skill in ("task-team-lead", "draw-figure"):
            with self.subTest(skill=skill):
                self.assertIsNone(hook.messaging_message(event(skill), self.skills))

    def test_task_team_messagingのSKILL_mdが無ければ何も渡さない(self):
        self.assertIsNone(hook.messaging_message(event("task-team-se"), self.skills))

    def test_渡す本文から先頭のfrontmatterを除く(self):
        self.put_skill()
        message = hook.messaging_message(event("task-team-pg"), self.skills)
        self.assertNotIn("description:", message)
        self.assertNotIn("---", message)


if __name__ == "__main__":
    unittest.main()

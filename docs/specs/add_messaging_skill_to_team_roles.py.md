# add_messaging_skill_to_team_roles.py

## ADR

- 0071-1 道具を使った直後に例外なくする作業は、プロンプトに書かずにフックに任せる

## 動き

- skill `task-team-se`・`task-team-pg`・`task-team-qa` を読んだ直後に動く。ほかの skill と道具の後には、何もしない。
- `${CLAUDE_CONFIG_DIR:-~/.claude}/skills/task-team-messaging/SKILL.md` の、先頭の `---` で囲んだ所を除いた本文を、「skill `task-team-messaging` も読む。」の次の行から続けて Claude に知らせる。
- そのファイルが無ければ、何もしない。

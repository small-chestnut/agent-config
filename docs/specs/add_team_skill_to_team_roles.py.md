# add_team_skill_to_team_roles.py

## ADR

- 0071-1 道具を使った直後に例外なくする作業は、プロンプトに書かずにフックに任せる
- 0083-1 役割の受け持ちと全役割が守る規則は共通の skill `task-team` に置き、役割の skill にはその役割でだけ要る規則を置く

## 動き

- skill `task-team-lead`・`task-team-se`・`task-team-pg`・`task-team-qa` を読んだ直後に、`${CLAUDE_CONFIG_DIR:-~/.claude}/skills/task-team/SKILL.md` の、先頭の `---` で囲んだ所を除いた本文を、「skill `task-team` も読む。」の次の行から続けて Claude に知らせる。
- ほかの skill とツールの後には、何もしない。
- そのファイルが無ければ、何もしない。

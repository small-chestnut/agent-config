"""PL・SE・PG・QA の skill を読んだ直後に、skill task-team の本文を Claude に渡す(Claude Code の PostToolUse フック。ADR 0071-1・0083-1)。

tool_name が Skill で、tool_input.skill が task-team-lead・task-team-se・task-team-pg・task-team-qa のどれかのときだけ動く。
${CLAUDE_CONFIG_DIR:-~/.claude}/skills/task-team/SKILL.md の、先頭の --- で囲んだ所を除いた本文を、
「skill `task-team` も読む。」の次の行から続けて additionalContext で知らせ、exit 0 で終わる。
そのファイルが無ければ何もしない。
"""
import json
import os
import sys
from pathlib import Path

ROLE_SKILLS = ("task-team-lead", "task-team-se", "task-team-pg", "task-team-qa")
TEAM = "task-team"


def config_dir() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def strip_front_matter(text: str) -> str:
    """先頭の --- で囲んだ所を除く。"""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1:]).lstrip("\n")
    return text


def team_message(event: dict, skills_dir: Path | None = None) -> str | None:
    """渡す文。何もしないときは None。skills_dir は skill のフォルダ(テストで差し替える)。"""
    if event.get("tool_name") != "Skill":
        return None
    if (event.get("tool_input") or {}).get("skill") not in ROLE_SKILLS:
        return None
    skills_dir = skills_dir or config_dir() / "skills"
    path = skills_dir / TEAM / "SKILL.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    return f"skill `{TEAM}` も読む。\n{strip_front_matter(text)}"


def main() -> int:
    try:
        event = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return 0
    message = team_message(event)
    if message is None:
        return 0
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                             "additionalContext": message}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

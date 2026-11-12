"""SE のセッションを起こした直後に、ピン留めするよう Claude に知らせる(Claude Code の PostToolUse フック。ADR 0071-1・0057-2)。

tool_name が mcp__ccd_session__start_session で、tool_input.name が -se で終わるときだけ、
「起こした SE を、`set_pinned` でピン留めする。(ADR 0057-2)」を additionalContext で知らせ、exit 0 で終わる。
"""
import json
import sys

START_SESSION = "mcp__ccd_session__start_session"
MESSAGE = "起こした SE を、`set_pinned` でピン留めする。(ADR 0057-2)"


def pin_message(event: dict) -> str | None:
    """知らせる文。何もしないときは None。"""
    if event.get("tool_name") != START_SESSION:
        return None
    name = (event.get("tool_input") or {}).get("name")
    if isinstance(name, str) and name.endswith("-se"):
        return MESSAGE
    return None


def main() -> int:
    try:
        event = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return 0
    message = pin_message(event)
    if message is None:
        return 0
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                             "additionalContext": message}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

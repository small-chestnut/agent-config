"""プロンプトと自動メモリを保存したときに、この保存で足した行を並べ、2つ(消しても意味が変わらない語・具体例や出来事の並び)を問う(Claude Code の PostToolUse フック)。

プロンプトと自動メモリ、足された行の取り方は check_rule_length.py と同じ。
問う行は、足された行のうち、この保存で書いた文字列(Edit・MultiEdit の new_string、Write の content)を含む行。
空の行とコードブロックの中は除く。問う行があれば stderr に並べて exit 2(Claude に返る)。
"""
import json
import sys
from pathlib import Path

from check_rule_length import read_rule_document, written_text

# 問いの文は、ここの1か所にだけ置く(check_rule_documents_changed_by_shell.py も import して使う)。(ADR 0055-2)
QUESTIONS = (
    "  1. 消しても意味が変わらない語は、消す。\n"
    "  2. 言いたい決まりや事実を1文で言わずに、具体例や出来事を並べている所は、それらがみなそこから出てくる状態の1文に替える。"
)


def asked_lines(text: str, new_lines: set[int] | None, written: str) -> list[tuple[int, str]]:
    """問う行 [(行番号, 行)]。new_lines が None なら全部の行が足された行。"""
    pieces = [s for s in (line.strip() for line in written.splitlines()) if s]
    out = []
    fence = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        body = line.strip()
        if fence or not body or (new_lines is not None and n not in new_lines):
            continue
        if any(p in body for p in pieces):
            out.append((n, body))
    return out


def main() -> int:
    try:
        event = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return 0
    tool_input = event.get("tool_input") or {}
    file_path = tool_input.get("file_path")
    if not file_path or not Path(file_path).is_file():
        return 0
    doc = read_rule_document(Path(file_path), tool_input)
    if doc is None:
        return 0
    rel, text, new_lines = doc
    found = asked_lines(text, new_lines, written_text(tool_input))
    if not found:
        return 0
    sys.stderr.reconfigure(encoding="utf-8")
    print("この保存で足した行です。行ごとに次の2つを確かめ、当たる所を直してください:", file=sys.stderr)
    print(QUESTIONS, file=sys.stderr)
    for n, body in found:
        print(f"  {rel}:{n}  {body}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

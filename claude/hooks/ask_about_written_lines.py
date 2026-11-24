"""プロンプトと自動メモリを保存したときに、この保存で足した行を並べ、2つ(消しても意味が変わらない語・具体例や出来事の並び)と、段の見出しがあれば段の導き方を問う(Claude Code の PostToolUse フック)。

プロンプトと自動メモリの決め方、足された行の取り方は rule_document_added_lines.py にある。
問う行は、足された行のうち、この保存で書いた文字列(Edit・MultiEdit の new_string、Write の content)を含む行。
空の行とコードブロックの中は除く。問う行があれば stderr に並べて exit 2(Claude に返る)。
"""
import json
import re
import sys
from pathlib import Path

from rule_document_added_lines import read_rule_document, written_text

# 問いの文は、ここの1か所にだけ置く(check_rule_documents_changed_by_shell.py も import して使う)。(ADR 0055-2)
QUESTIONS = (
    "  1. 消しても意味が変わらない語は、消す。\n"
    "  2. 言いたい決まりや事実を1文で言わずに、具体例や出来事を並べている所は、それらがみなそこから出てくる状態の1文に替える。"
)
# 段の見出しの行があるときだけ足す問い。(ADR 0061-1・0095-1・0098-2)
LAYER_QUESTION = "  3. 原則・目的の見出しは、skill `prompt-structure` の段の書き方に照らし、合わない所を直す。"
LAYER_HEADING = re.compile(r"^(?:# 原則|## 目的)")


def questions_for(bodies: list[str]) -> str:
    """問う行の本文の並びに出す問いの文。段の見出しがあれば段の問いを足す。"""
    if any(LAYER_HEADING.match(body) for body in bodies):
        return QUESTIONS + "\n" + LAYER_QUESTION
    return QUESTIONS


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
    print("この保存で足した行です。行ごとに次の問いを確かめ、当たる所を直してください:", file=sys.stderr)
    print(questions_for([body for _, body in found]), file=sys.stderr)
    for n, body in found:
        print(f"  {rel}:{n}  {body}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

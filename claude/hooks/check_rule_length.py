"""決まりの文書を保存したときに、新しく足した決まりの1行の字数を数える(Claude Code の PostToolUse フック)。

決まりの文書は、名前が CLAUDE.md・AGENTS.md・SKILL.md のファイルと、リポジトリの
.claude/rule-documents.txt に1行ずつ書いた glob(リポジトリの根から)に当たるファイル。
決まりの1行は、その箇条書き(「- 」で始まる行。コードブロックの中は除く)。
新しく足した行は、HEAD との差分で足された行。git にまだ入っていない文書は全部の行。
字数は「- 」と行頭の空白を除いて数え、`…` で囲んだコードは1字と数える。
上限を超えた行があれば stderr に並べて exit 2(Claude に返る)。git の外のファイルは数えない。
"""
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

LIMIT = 60
RULE_DOCUMENT_NAMES = ("CLAUDE.md", "AGENTS.md", "SKILL.md")
PROJECT_LIST = Path(".claude") / "rule-documents.txt"

BULLET = re.compile(r"^\s*- (.*)$")
CODE = re.compile(r"`[^`]*`")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def rule_length(body: str) -> int:
    """決まりの1行(「- 」の後ろ)の字数。`…` で囲んだコードは1字。"""
    return len(CODE.sub("x", body))


def rule_lines(text: str) -> dict[int, str]:
    """文書の中の決まりの行 {行番号: 「- 」の後ろ}。コードブロックの中は除く。"""
    rules = {}
    fence = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        m = BULLET.match(line)
        if m and not fence:
            rules[n] = m.group(1)
    return rules


def added_line_numbers(diff: str) -> set[int]:
    """1つのファイルの `git diff -U0` の出力から、足された行の番号。"""
    added: set[int] = set()
    for line in diff.splitlines():
        m = HUNK.match(line)
        if m:
            start = int(m.group(1))
            count = int(m.group(2)) if m.group(2) is not None else 1
            added.update(range(start, start + count))
    return added


def too_long(text: str, new_lines: set[int] | None, limit: int = LIMIT) -> list[tuple[int, int, str]]:
    """新しい決まりの行のうち上限を超えたもの [(行番号, 字数, 本文)]。new_lines が None なら全部の行。"""
    out = []
    for n, body in rule_lines(text).items():
        if new_lines is not None and n not in new_lines:
            continue
        length = rule_length(body)
        if length > limit:
            out.append((n, length, body))
    return out


def is_rule_document(rel: str, patterns: list[str]) -> bool:
    """リポジトリの根からのパス rel が決まりの文書か。"""
    return Path(rel).name in RULE_DOCUMENT_NAMES or any(fnmatch.fnmatch(rel, p) for p in patterns)


def read_patterns(text: str) -> list[str]:
    """rule-documents.txt の中身から glob の一覧(空行と # の行は除く)。"""
    return [s for s in (line.strip() for line in text.splitlines()) if s and not s.startswith("#")]


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=cwd,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def check(path: Path) -> list[str]:
    """保存されたファイルを数え、上限を超えた行の知らせ。数えないファイルなら空。"""
    top = git(path.parent, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        return []
    root = Path(top.stdout.strip()).resolve()
    rel = path.resolve().relative_to(root).as_posix()
    listing = root / PROJECT_LIST
    patterns = read_patterns(listing.read_text(encoding="utf-8", errors="replace")) if listing.exists() else []
    if not is_rule_document(rel, patterns):
        return []
    new_lines = None
    if git(root, "ls-files", "--error-unmatch", "--", rel).returncode == 0:
        diff = git(root, "diff", "-U0", "HEAD", "--", rel)
        if diff.returncode == 0:
            new_lines = added_line_numbers(diff.stdout)
    text = path.read_text(encoding="utf-8", errors="replace")
    return [f"{rel}:{n}  {length}字  {body}" for n, length, body in too_long(text, new_lines)]


def main() -> int:
    try:
        event = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return 0
    file_path = (event.get("tool_input") or {}).get("file_path")
    if not file_path or not Path(file_path).is_file():
        return 0
    found = check(Path(file_path))
    if not found:
        return 0
    sys.stderr.reconfigure(encoding="utf-8")
    print(f"決まりの1行が上限 {LIMIT} 字を超えています(`…` のコードは1字と数えます)。短くしてください:",
          file=sys.stderr)
    for f in found:
        print("  " + f, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

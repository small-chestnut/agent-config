"""プロンプトと自動メモリを見分け、保存で足された行を取る(ask_about_written_lines.py と check_rule_documents_changed_by_shell.py が import して使う)。

プロンプトは、名前が CLAUDE.md・AGENTS.md・SKILL.md のファイルと、リポジトリの
.claude/rule-documents.txt に1行ずつ書いた glob(リポジトリのルートから)に当たるファイル。
足された行は、HEAD との差分で足された行。git にまだ入っていない文書は全部の行。
自動メモリ(設定ディレクトリの projects/<プロジェクト>/memory/ の下の md)の足された行は、HEAD との差分でなく、
この保存の tool_input から決める。自動メモリのほかの、git の外のファイルは取らない。
"""
import fnmatch
import os
import re
import subprocess
from pathlib import Path

RULE_DOCUMENT_NAMES = ("CLAUDE.md", "AGENTS.md", "SKILL.md")
PROJECT_LIST = Path(".claude") / "rule-documents.txt"

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


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


def is_rule_document(rel: str, patterns: list[str]) -> bool:
    """リポジトリのルートからのパス rel がプロンプトか。"""
    return Path(rel).name in RULE_DOCUMENT_NAMES or any(fnmatch.fnmatch(rel, p) for p in patterns)


def read_patterns(text: str) -> list[str]:
    """rule-documents.txt の中身から glob の一覧(空行と # の行は除く)。"""
    return [s for s in (line.strip() for line in text.splitlines()) if s and not s.startswith("#")]


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=cwd,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def is_memory(path: Path) -> bool:
    """path が自動メモリか。設定ディレクトリ(CLAUDE_CONFIG_DIR、無ければ ~/.claude)の
    projects/<プロジェクト>/memory/ の下の md。リンクはたどらずに比べる。(ADR 0055-1)"""
    config = os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude")
    try:
        rel = Path(os.path.normcase(os.path.abspath(path))).relative_to(os.path.normcase(os.path.abspath(config)))
    except ValueError:
        return False
    parts = rel.parts
    return len(parts) >= 4 and parts[0] == "projects" and parts[2] == "memory" and parts[-1].endswith(".md")


def written_text(tool_input: dict) -> str:
    """この保存で書いた文字列。"""
    edits = tool_input.get("edits") or [tool_input]
    parts = [e.get("new_string") or "" for e in edits] + [tool_input.get("content") or ""]
    return "\n".join(parts)


def occurrences(text: str, needle: str) -> list[int]:
    """text の中で needle が現れる位置すべて。"""
    out, i = [], text.find(needle)
    while i != -1:
        out.append(i)
        i = text.find(needle, i + 1)
    return out


def memory_added_lines(text: str, tool_input: dict) -> set[int] | None:
    """自動メモリの、この保存で足した行の番号。Write は None(全部の行)。
    Edit・MultiEdit は、new_string が掛かる行のうち、本文が old_string のどの行とも違う行。"""
    if "content" in tool_input and "new_string" not in tool_input and "edits" not in tool_input:
        return None
    lines = text.split("\n")
    starts = [0]
    for line in lines[:-1]:
        starts.append(starts[-1] + len(line) + 1)

    def line_of(pos: int) -> int:
        return max(i for i, s in enumerate(starts) if s <= pos)

    added: set[int] = set()
    for edit in tool_input.get("edits") or [tool_input]:
        new = (edit.get("new_string") or "").strip("\n")
        if not new.strip():
            continue
        old_bodies = {line.strip() for line in (edit.get("old_string") or "").splitlines()}
        found = occurrences(text, new)
        if len(found) > 1 and not edit.get("replace_all"):
            # 前後が行の境目に当たる所が1つだけなら、そこが書いた所。決まらなければ、現れる所をみな書いた所とする
            whole = [p for p in found
                     if (p == 0 or text[p - 1] == "\n") and (p + len(new) == len(text) or text[p + len(new)] == "\n")]
            if len(whole) == 1:
                found = whole
        for pos in found:
            for n in range(line_of(pos), line_of(pos + len(new) - 1) + 1):
                body = lines[n].strip()
                if body and body not in old_bodies:
                    added.add(n + 1)
    return added


def read_rule_document(path: Path, tool_input: dict | None = None) -> tuple[str, str, set[int] | None] | None:
    """保存されたファイルが git の中のプロンプトか自動メモリなら (ルートからのパス, 中身, 足された行の番号)。
    足された行の番号は、git にまだ入っていない文書か、自動メモリの Write なら None(全部の行)。"""
    if is_memory(path):
        text = path.read_text(encoding="utf-8", errors="replace")
        return path.as_posix(), text, memory_added_lines(text, tool_input or {})
    top = git(path.parent, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        return None
    root = Path(top.stdout.strip()).resolve()
    rel = path.resolve().relative_to(root).as_posix()
    listing = root / PROJECT_LIST
    patterns = read_patterns(listing.read_text(encoding="utf-8", errors="replace")) if listing.exists() else []
    if not is_rule_document(rel, patterns):
        return None
    new_lines = None
    if git(root, "ls-files", "--error-unmatch", "--", rel).returncode == 0:
        diff = git(root, "diff", "-U0", "HEAD", "--", rel)
        if diff.returncode == 0:
            new_lines = added_line_numbers(diff.stdout)
    return rel, path.read_text(encoding="utf-8", errors="replace"), new_lines

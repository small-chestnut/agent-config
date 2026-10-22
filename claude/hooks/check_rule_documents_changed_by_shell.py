"""Bash・PowerShell のコマンドで書き換えた決まりの文書にも、字数の数えと消せる語の問いを掛ける(Claude Code の PreToolUse と PostToolUse のフック)。

check_rule_length.py と ask_removable_words.py は Edit・Write・MultiEdit にだけ掛かるため、
シェルから書いた行はどちらも通らない。そこでコマンドの前後で決まりの文書を見比べる。
  before(PreToolUse):  決まりの文書の中身を一時ファイルに写す
  after(PostToolUse):  写しと今の中身を比べ、このコマンドで足された行を数え、問う
見るリポジトリは、フックの cwd と、コマンドに書かれた絶対パス(C:/…・C:\\…・/c/…・~/…)が入っているもの。
決まりの文書の決め方・字数の数え方は check_rule_length.py と同じ。知らせがあれば stderr に並べて exit 2。
"""
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from difflib import SequenceMatcher
from pathlib import Path

from check_rule_length import LIMIT, PROJECT_LIST, git, is_rule_document, read_patterns, too_long

SNAPSHOT_DIR = Path(tempfile.gettempdir()) / "claude-rule-document-snapshots"
SNAPSHOT_LIFETIME = 24 * 60 * 60
MAX_REPOSITORIES = 8

WINDOWS_PATH = re.compile(r"[A-Za-z]:[\\/][^\s\"'`;|&<>()]*")
GIT_BASH_PATH = re.compile(r"(?<![\w.])/([a-zA-Z])/[^\s\"'`;|&<>()]*")
HOME_PATH = re.compile(r"(?:~|\$HOME|\$env:USERPROFILE)[\\/][^\s\"'`;|&<>()]*")


def paths_in_command(command: str) -> list[Path]:
    """コマンドに書かれた絶対パス。"""
    out = [Path(m) for m in WINDOWS_PATH.findall(command)]
    out += [Path(f"{m.group(1).upper()}:/{m.group(0)[3:]}") for m in GIT_BASH_PATH.finditer(command)]
    home = Path.home()
    out += [home / re.split(r"[\\/]", m, maxsplit=1)[1] for m in HOME_PATH.findall(command)]
    return out


def repository_root(path: Path) -> Path | None:
    """path が入っている git リポジトリの根。path が無ければ、ある所まで親へ上る。"""
    for p in (path, *path.parents):
        if p.is_dir():
            top = git(p, "rev-parse", "--show-toplevel")
            return Path(top.stdout.strip()).resolve() if top.returncode == 0 else None
    return None


def repositories(cwd: str | None, command: str) -> list[Path]:
    roots: list[Path] = []
    for p in ([Path(cwd)] if cwd else []) + paths_in_command(command):
        root = repository_root(p)
        if root and root not in roots:
            roots.append(root)
    return roots[:MAX_REPOSITORIES]


def rule_documents(root: Path) -> dict[str, str]:
    """リポジトリの中の決まりの文書 {根からのパス: 中身}。git が無視するファイルは除く。"""
    listing = root / PROJECT_LIST
    patterns = read_patterns(listing.read_text(encoding="utf-8", errors="replace")) if listing.exists() else []
    files = git(root, "ls-files", "-co", "--exclude-standard")
    docs = {}
    for rel in files.stdout.splitlines():
        if is_rule_document(rel, patterns) and (root / rel).is_file():
            docs[rel] = (root / rel).read_text(encoding="utf-8", errors="replace")
    return docs


def added_lines(before: str, after: str) -> set[int]:
    """before から after で足された・書き換えられた行の番号(after の 1 始まり)。"""
    added: set[int] = set()
    matcher = SequenceMatcher(None, before.splitlines(), after.splitlines(), autojunk=False)
    for tag, _, _, j1, j2 in matcher.get_opcodes():
        if tag in ("replace", "insert"):
            added.update(range(j1 + 1, j2 + 1))
    return added


def asked_lines(text: str, new_lines: set[int]) -> list[tuple[int, str]]:
    """問う行 [(行番号, 行)]。空の行とコードブロックの中は除く。"""
    out = []
    fence = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if not fence and line.strip() and n in new_lines:
            out.append((n, line.strip()))
    return out


def findings(before: dict[str, dict[str, str]], roots: list[Path]) -> tuple[list[str], list[str]]:
    """(上限を超えた行の知らせ, 問う行)。before は {リポジトリの根: {根からのパス: 中身}}。"""
    long_lines, asked = [], []
    for root in roots:
        old = before.get(str(root), {})
        for rel, text in rule_documents(root).items():
            if old.get(rel) == text:
                continue
            new_lines = added_lines(old.get(rel, ""), text)
            long_lines += [f"{rel}:{n}  {length}字  {body}" for n, length, body in too_long(text, new_lines)]
            asked += [f"{rel}:{n}  {body}" for n, body in asked_lines(text, new_lines)]
    return long_lines, asked


def snapshot_path(event: dict) -> Path:
    key = event.get("tool_use_id") or json.dumps(event.get("tool_input"), sort_keys=True)
    name = hashlib.sha256(f"{event.get('session_id')}:{key}".encode("utf-8")).hexdigest()[:32]
    return SNAPSHOT_DIR / f"{name}.json"


def remove_old_snapshots(now: float) -> None:
    """失敗したコマンドの写しは after が読まないので、1日たったものを消す。"""
    for p in SNAPSHOT_DIR.glob("*.json"):
        if now - p.stat().st_mtime > SNAPSHOT_LIFETIME:
            p.unlink(missing_ok=True)


def before_command(event: dict) -> int:
    roots = repositories(event.get("cwd"), (event.get("tool_input") or {}).get("command") or "")
    if not roots:
        return 0
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    remove_old_snapshots(time.time())
    snapshot = {str(root): rule_documents(root) for root in roots}
    snapshot_path(event).write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
    return 0


def after_command(event: dict) -> int:
    path = snapshot_path(event)
    if not path.is_file():
        return 0
    before = json.loads(path.read_text(encoding="utf-8"))
    os.remove(path)
    long_lines, asked = findings(before, [Path(r) for r in before])
    if not long_lines and not asked:
        return 0
    sys.stderr.reconfigure(encoding="utf-8")
    if long_lines:
        print(f"このコマンドで足した決まりの1行が上限 {LIMIT} 字を超えています(`…` のコードは1字と数えます)。短くしてください:",
              file=sys.stderr)
        for f in long_lines:
            print("  " + f, file=sys.stderr)
    if asked:
        print("このコマンドで決まりの文書に足した行です。行ごとに、消しても意味が変わらない語を探し、あれば消してください:",
              file=sys.stderr)
        for f in asked:
            print("  " + f, file=sys.stderr)
    return 2


def main() -> int:
    try:
        event = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return 0
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "before":
        try:
            return before_command(event)
        except Exception:
            return 0   # 写しに失敗しても、コマンドは止めない
    if mode == "after":
        return after_command(event)
    return 0


if __name__ == "__main__":
    sys.exit(main())

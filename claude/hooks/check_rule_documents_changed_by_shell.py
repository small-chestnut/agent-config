"""Bash・PowerShell のコマンドで書き換えたプロンプトにも、字数の数えと消せる語の問いを掛ける(Claude Code の PreToolUse と PostToolUse のフック)。

check_rule_length.py と ask_removable_words.py は Edit・Write・MultiEdit にだけ掛かるため、
シェルから書いた行はどちらも通らない。そこでコマンドの前後でプロンプトを見比べる。
  before(PreToolUse):  プロンプトの中身のスナップショットを一時ファイルに取る
  after(PostToolUse):  スナップショットと今の中身を比べ、このコマンドで足された行を数え、問う
  record(PreToolUse の Edit・Write・MultiEdit):  書こうとしている行を、書きかけの記録に取る(ADR 0041-1)
  confirm(PostToolUse の Edit・Write・MultiEdit):  書けた呼び出しの記録を、書けた記録にする。after は書けた記録の行を除く
見るリポジトリは、フックの cwd と、コマンドに書かれた絶対パス(C:/…・C:\\…・/c/…・~/…)が入っているもの。
プロンプトの決め方・字数の数え方は check_rule_length.py と同じ。知らせがあれば stderr に並べて exit 2。
取り込むコマンド(git merge など)では、HEAD かインデックスと同じ行と衝突の印の行は問わない。
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
WRITTEN_DIR = SNAPSHOT_DIR / "written"
SNAPSHOT_LIFETIME = 24 * 60 * 60
MAX_REPOSITORIES = 8

WINDOWS_PATH = re.compile(r"[A-Za-z]:[\\/][^\s\"'`;|&<>()]*")
GIT_BASH_PATH = re.compile(r"(?<![\w.])/([a-zA-Z])/[^\s\"'`;|&<>()]*")
HOME_PATH = re.compile(r"(?:~|\$HOME|\$env:USERPROFILE)[\\/][^\s\"'`;|&<>()]*")

IMPORTING_SUBCOMMANDS = "merge|pull|checkout|switch|rebase|cherry-pick|reset|restore|revert|am"
IMPORTING_COMMAND = re.compile(
    r"\bgit(?:\s+(?:-C\s+\S+|-c\s+\S+|--[\w-]+(?:=\S+)?))*\s+(?:" + IMPORTING_SUBCOMMANDS + r")(?=[\s;&|)]|$)")
CONFLICT_MARKER = re.compile(r"^(?:<<<<<<<|=======|>>>>>>>|\|\|\|\|\|\|\|)(?:\s|$)")


def paths_in_command(command: str) -> list[Path]:
    """コマンドに書かれた絶対パス。"""
    out = [Path(m) for m in WINDOWS_PATH.findall(command)]
    out += [Path(f"{m.group(1).upper()}:/{m.group(0)[3:]}") for m in GIT_BASH_PATH.finditer(command)]
    home = Path.home()
    out += [home / re.split(r"[\\/]", m, maxsplit=1)[1] for m in HOME_PATH.findall(command)]
    return out


def repository_root(path: Path) -> Path | None:
    """path が入っている git リポジトリのルート。path が無ければ、ある所まで親へ上る。"""
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


def project_patterns(root: Path) -> list[str]:
    """リポジトリの .claude/rule-documents.txt に書かれたプロンプトの glob。"""
    listing = root / PROJECT_LIST
    return read_patterns(listing.read_text(encoding="utf-8", errors="replace")) if listing.exists() else []


def rule_documents(root: Path) -> dict[str, str]:
    """リポジトリの中のプロンプト {ルートからのパス: 中身}。git が無視するファイルは除く。"""
    patterns = project_patterns(root)
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


def brings_other_commits(command: str) -> bool:
    """command が、git がほかのコミットの中身を持ってくるコマンドを含むか。"""
    return bool(IMPORTING_COMMAND.search(command))


def git_versions(root: Path, rel: str) -> list[str]:
    """HEAD とインデックス(段階 0〜3)にある rel の中身のうち、取れたもの。"""
    out = []
    for spec in (f"HEAD:{rel}", *(f":{n}:{rel}" for n in range(4))):
        shown = git(root, "show", spec)
        if shown.returncode == 0:
            out.append(shown.stdout)
    return out


def imported_lines(text: str, versions: list[str]) -> set[int]:
    """text の行のうち、git が持ってきた行(どれかの版と同じ行)と衝突の印の行の番号。"""
    lines = text.splitlines()
    imported = {n for n, line in enumerate(lines, 1) if CONFLICT_MARKER.match(line)}
    for version in versions:
        imported |= set(range(1, len(lines) + 1)) - added_lines(version, text)
    return imported


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


def findings(before: dict[str, dict[str, str]], roots: list[Path], command: str) -> tuple[list[str], list[str]]:
    """(上限を超えた行の知らせ, 問う行)。before は {リポジトリのルート: {ルートからのパス: 中身}}。"""
    long_lines, asked = [], []
    for root in roots:
        old = before.get(str(root), {})
        for rel, text in rule_documents(root).items():
            if old.get(rel) == text:
                continue
            new_lines = added_lines(old.get(rel, ""), text)
            if brings_other_commits(command):
                new_lines -= imported_lines(text, git_versions(root, rel))
            new_lines -= lines_matching(text, written_lines(root / rel))
            long_lines += [f"{rel}:{n}  {length}字  {body}" for n, length, body in too_long(text, new_lines)]
            asked += [f"{rel}:{n}  {body}" for n, body in asked_lines(text, new_lines)]
    return long_lines, asked


def lines_matching(text: str, bodies: set[str]) -> set[int]:
    """text の行のうち、bodies のどれかと同じ行の番号。"""
    return {n for n, line in enumerate(text.splitlines(), 1) if line in bodies}


def written_prefix(path: Path) -> str:
    """書き込み記録の名前の頭。ファイルのパスで決まる。"""
    return hashlib.sha256(os.path.normcase(str(path.resolve())).encode("utf-8")).hexdigest()[:16]


def written_path(event: dict, path: Path, pending: bool) -> Path:
    key = hashlib.sha256(f"{event.get('session_id')}:{event.get('tool_use_id')}".encode("utf-8")).hexdigest()[:16]
    return WRITTEN_DIR / f"{written_prefix(path)}-{key}{'.pending' if pending else ''}.json"


def written_lines(path: Path) -> set[str]:
    """path に Edit・Write・MultiEdit が書けた行の本文。"""
    out: set[str] = set()
    for p in WRITTEN_DIR.glob(f"{written_prefix(path)}-*.json"):
        if not p.name.endswith(".pending.json"):
            out.update(json.loads(p.read_text(encoding="utf-8"))["lines"])
    return out


def snapshot_path(event: dict) -> Path:
    key = event.get("tool_use_id") or json.dumps(event.get("tool_input"), sort_keys=True)
    name = hashlib.sha256(f"{event.get('session_id')}:{key}".encode("utf-8")).hexdigest()[:32]
    return SNAPSHOT_DIR / f"{name}.json"


def remove_old_snapshots(now: float) -> None:
    """失敗したコマンドのスナップショットは after が読まないので、1日たったものを消す。"""
    for p in (*SNAPSHOT_DIR.glob("*.json"), *WRITTEN_DIR.glob("*.json")):
        if now - p.stat().st_mtime > SNAPSHOT_LIFETIME:
            p.unlink(missing_ok=True)


def written_content(current: str, tool_name: str, tool_input: dict) -> str | None:
    """Edit・Write・MultiEdit が書いた後の中身。当てられなければ None。"""
    if tool_name == "Write":
        return tool_input["content"]
    edits = tool_input["edits"] if tool_name == "MultiEdit" else [tool_input]
    for edit in edits:
        old, new = edit["old_string"], edit["new_string"]
        if old == "":
            if current != "":
                return None
            current = new
        elif old in current:
            current = current.replace(old, new)
        else:
            return None
    return current


def is_prompt_file(path: Path) -> bool:
    """path(まだ無くてもよい)が、git の中にあり、git が無視せず、プロンプトの名前に当たるか。"""
    root = repository_root(path.parent)
    if root is None:
        return False
    rel = path.resolve().relative_to(root).as_posix()
    patterns = project_patterns(root)
    return is_rule_document(rel, patterns) and git(root, "check-ignore", "-q", "--", rel).returncode != 0


def record_written(event: dict) -> int:
    tool_input = event.get("tool_input") or {}
    path = Path(tool_input["file_path"])
    if not is_prompt_file(path):
        return 0
    current = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
    after = written_content(current, event.get("tool_name"), tool_input)
    if after is None:
        return 0
    body = after.splitlines()
    WRITTEN_DIR.mkdir(parents=True, exist_ok=True)
    remove_old_snapshots(time.time())
    lines = [body[n - 1] for n in sorted(added_lines(current, after))]
    written_path(event, path, pending=True).write_text(json.dumps({"lines": lines}, ensure_ascii=False), encoding="utf-8")
    return 0


def confirm_written(event: dict) -> int:
    path = Path((event.get("tool_input") or {})["file_path"])
    pending = written_path(event, path, pending=True)
    if pending.is_file():
        os.replace(pending, written_path(event, path, pending=False))
    return 0


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
    command = (event.get("tool_input") or {}).get("command") or ""
    long_lines, asked = findings(before, [Path(r) for r in before], command)
    if not long_lines and not asked:
        return 0
    sys.stderr.reconfigure(encoding="utf-8")
    if long_lines:
        print(f"このコマンドで足した決まりの1行が上限 {LIMIT} 字を超えています(`…` のコードは1字と数えます)。短くしてください:",
              file=sys.stderr)
        for f in long_lines:
            print("  " + f, file=sys.stderr)
    if asked:
        print("このコマンドでプロンプトに足した行です。行ごとに、消しても意味が変わらない語を探し、あれば消してください:",
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
            return 0   # スナップショットに失敗しても、コマンドは止めない
    if mode == "after":
        return after_command(event)
    if mode in ("record", "confirm"):
        try:
            return (record_written if mode == "record" else confirm_written)(event)
        except Exception:
            return 0   # Edit・Write・MultiEdit は、記録に失敗しても止めない
    return 0


if __name__ == "__main__":
    sys.exit(main())

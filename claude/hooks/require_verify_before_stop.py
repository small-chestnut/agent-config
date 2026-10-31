"""ターンの終わりに、今の中身で確かめのコマンドが通っているかを見る(Claude Code の Stop フック)。(ADR 0011-1)

引数: turn-start(UserPromptSubmit)・record(PostToolUse の Bash|PowerShell)・stop(Stop)。
ターンの始めの中身の印を記録し、確かめのコマンドが通るたびに、そのときの中身の印へ通ったと記録し、
ターンの終わりに、中身が変わったのに今の中身で通っていない確かめがあれば、並べて exit 2 で止める。
フックはコマンドを走らせない。一覧の無いリポジトリと git の外では何もしない。
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

VERIFY_COMMANDS_PATH = ".claude/verify-commands.txt"  # (ADR 0011-2)
RECORD_NAME = "claude-verify.json"
KEEP = 50
LOCK_WAIT = 5.0
LOCK_STALE = 30.0
LOCK_INTERVAL = 0.05
SEPARATORS = re.compile(r"[|;&\n]")


def read_commands(text: str) -> list[str]:
    """確かめのコマンドの一覧から、頭を読む。空の行と # で始まる行は読まない。"""
    heads = []
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            heads.append(line)
    return heads


def counted_heads(command: str, background: bool, heads: list[str]) -> list[str]:
    """このコマンドが通ったときに、通ったと数える頭。"""
    if background:
        return []
    command = command.strip()
    if SEPARATORS.search(command.replace("2>&1", "")):
        return []
    return [h for h in heads if command == h or command.startswith(h + " ") or command.startswith(h + "\t")]


def unpassed_heads(start_sig: str | None, now_sig: str, passed: dict, heads: list[str]) -> list[str]:
    """止めるときに並べる、今の中身で通っていない頭。止めないなら空。"""
    if not start_sig or start_sig == now_sig:
        return []
    done = passed.get(now_sig, [])
    return [h for h in heads if h not in done]


def load_record(path: Path) -> dict:
    """確かめの記録。読めないか壊れていれば空。"""
    empty = {"turn_start": {}, "passed": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return empty
        for key in empty:
            if not isinstance(data.get(key), dict):
                data[key] = {}
        return data
    except (OSError, ValueError):
        return empty


def put_latest(d: dict, key: str, value) -> None:
    """辞書の最後に入れる。既にあるキーも最後に動かし、trim で古い方として捨てられないようにする。"""
    d.pop(key, None)
    d[key] = value


def trim(record: dict) -> dict:
    for key in ("turn_start", "passed"):
        d = record[key]
        while len(d) > KEEP:
            del d[next(iter(d))]
    return record


def update_record(path: Path, mutate, wait: float = LOCK_WAIT, stale: float = LOCK_STALE) -> bool:
    """ロックを持って、記録を読み、mutate で直し、書き戻す。ロックが取れなければ書かずに False。"""
    lock = path.with_name(path.name + ".lock")
    deadline = time.monotonic() + wait
    while True:
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            break
        except FileExistsError:
            try:
                if time.time() - lock.stat().st_mtime > stale:
                    lock.unlink()
                    continue
            except OSError:
                continue
            if time.monotonic() >= deadline:
                return False
            time.sleep(LOCK_INTERVAL)
    try:
        record = load_record(path)
        mutate(record)
        trim(record)
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=RECORD_NAME, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False)
        os.replace(tmp, path)
        return True
    finally:
        try:
            lock.unlink()
        except OSError:
            pass


def git(args: list[str], cwd: str, env: dict | None = None) -> str:
    out = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", check=True)
    return out.stdout.strip()


def content_sig(root: str) -> str:
    """docs/ を除いた作業ツリーの中身から作る git の tree の id。本物の index は変えない。"""
    index = Path(git(["rev-parse", "--path-format=absolute", "--git-path", "index"], root))
    fd, tmp = tempfile.mkstemp(prefix="claude-verify-index")
    os.close(fd)
    try:
        if index.exists():
            Path(tmp).write_bytes(index.read_bytes())
        else:
            os.unlink(tmp)
        env = {**os.environ, "GIT_INDEX_FILE": tmp}
        git(["add", "-A"], root, env)
        git(["rm", "-r", "--cached", "-q", "--ignore-unmatch", "--", "docs"], root, env)
        return git(["write-tree"], root, env)
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else ""
    data = json.loads(sys.stdin.read() or "{}")
    cwd = data.get("cwd") or os.getcwd()
    root = git(["rev-parse", "--show-toplevel"], cwd)
    list_path = Path(root) / VERIFY_COMMANDS_PATH
    if not list_path.is_file():
        return 0
    heads = read_commands(list_path.read_text(encoding="utf-8"))
    if not heads:
        return 0
    common = Path(git(["rev-parse", "--path-format=absolute", "--git-common-dir"], root))
    record_path = common / RECORD_NAME
    session = str(data.get("session_id", ""))

    if mode == "turn-start":
        sig = content_sig(root)
        update_record(record_path, lambda r: put_latest(r["turn_start"], session, sig))
    elif mode == "record":
        tool_input = data.get("tool_input") or {}
        hit = counted_heads(str(tool_input.get("command", "")), bool(tool_input.get("run_in_background")), heads)
        if hit:
            sig = content_sig(root)

            def add(r):
                have = r["passed"].pop(sig, [])
                r["passed"][sig] = have
                have.extend(h for h in hit if h not in have)

            update_record(record_path, add)
    elif mode == "stop":
        record = load_record(record_path)
        missing = unpassed_heads(record["turn_start"].get(session), content_sig(root), record["passed"], heads)
        if missing:
            lines = "\n".join(f"  {h}" for h in missing)
            message = (
                "このターンで中身が変わりましたが、今の中身で通っていない確かめのコマンドがあります。\n"
                "リポジトリの中で走らせて通してから終えてください(パイプ・;・&・バックグラウンドを付けると数えません):\n"
                f"{lines}\n"
            )
            sys.stderr.buffer.write(message.encode("utf-8"))
            sys.stderr.flush()
            return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception:
        sys.exit(0)

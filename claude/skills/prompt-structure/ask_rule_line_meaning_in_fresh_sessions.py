"""規則の1行を、決まりの文書を読まない3つの新しいセッションに読ませ、3つの答えを並べて出す。

仕様は docs/specs/ask_rule_line_meaning_in_fresh_sessions.py.md。ADR 0087-1。
使い方: python ask_rule_line_meaning_in_fresh_sessions.py "<規則の1行>" [--model <モデル>]
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

SESSIONS = 3
DEFAULT_MODEL = "claude-opus-5-5"
QUESTION = (
    "次の1行は、AI に守らせる決まりの文書の1行です。この1行だけを読んで、次の4つに短く答えてください。"
    "1. 何をする決まりか 2. 守っている例 3. 破っている例 4. 意味が1つに決まらない所"
)


def run_session(args, cwd, env, input_text):
    """claude を起動して input_text を標準入力に UTF-8 で渡して閉じ、(終了コード, 出力) を返す。"""
    done = subprocess.run(
        args, cwd=cwd, env=env, input=input_text,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return done.returncode, (done.stdout or "") + (done.stderr if done.returncode else "")


def session_args(claude, model):
    return [
        claude, "-p",
        "--model", model,
        "--setting-sources", "",
        "--disable-slash-commands",
        "--tools", "",
        "--no-session-persistence",
    ]


def main(argv, run_session=run_session, find_claude=shutil.which):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rule_line")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    options = parser.parse_args(argv)

    claude = find_claude("claude")
    if not claude:
        print("claude のコマンドが見つかりません。")
        return 1

    env = dict(os.environ)
    env["CLAUDE_CODE_DISABLE_CLAUDE_MDS"] = "1"
    args = session_args(claude, options.model)
    input_text = QUESTION + "\n\n" + options.rule_line

    folders = [tempfile.TemporaryDirectory() for _ in range(SESSIONS)]
    try:
        with ThreadPoolExecutor(max_workers=SESSIONS) as pool:
            results = list(pool.map(lambda f: run_session(args, f.name, env, input_text), folders))
    finally:
        for folder in folders:
            folder.cleanup()

    failed = [(n, code, output) for n, (code, output) in enumerate(results, start=1) if code != 0]
    for n, code, output in failed:
        print(f"## 答え{n} は終了コード {code} で終わりました\n{output}")
    if failed:
        return 1
    for n, (_, output) in enumerate(results, start=1):
        print(f"## 答え{n}\n{output.strip()}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

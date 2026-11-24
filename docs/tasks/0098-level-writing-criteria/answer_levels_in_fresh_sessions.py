"""全体の CLAUDE.md・rules/claude-md.md・skill prompt-structure を渡した新しいセッション5つに、各段に何を書くかを答えさせて並べる(R1-2)。

使い方(リポジトリのルートで): python docs/tasks/0098-level-writing-criteria/answer_levels_in_fresh_sessions.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "claude"
QUESTION = ("この決まりでは、命題・原則・目的・規則は、それぞれ何を書く段ですか。段ごとに1文で答えてください。"
            "段の名前と文だけの4行で出力してください。")
parts = [f"<{name}>\n{(ROOT / path).read_text(encoding='utf-8')}\n</{name}>" for name, path in (
    ("全体の CLAUDE.md", "CLAUDE.md"),
    ("rules/claude-md.md", "rules/claude-md.md"),
    ("skill prompt-structure", "skills/prompt-structure/SKILL.md"))]
TEXT = "\n\n".join(parts) + "\n\n" + QUESTION
ENV = {**os.environ, "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1"}


def answer(_):
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        r = subprocess.run([shutil.which("claude"), "-p", "--model", "claude-opus-5-5", "--setting-sources", "",
                            "--disable-slash-commands", "--tools", "", "--no-session-persistence"],
                           cwd=d, env=ENV, input=TEXT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout.strip() if r.returncode == 0 else "失敗: " + r.stderr + r.stdout


sys.stdout.reconfigure(encoding="utf-8")
with ThreadPoolExecutor(5) as pool:
    for n, text in enumerate(pool.map(answer, range(5)), 1):
        print(f"## 答え{n}\n{text}\n")

"""直した文書を新しいセッション3つずつに読ませ、命題と段の関係をどう答えるかを並べて出す(0097 の受け入れ条件 R1-1・R3-1・R3-2・R5-2)。

使い方: python docs/tasks/0097-state-derivation-in-claude-md/read_trial.py
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GLOBAL = (ROOT / "claude/CLAUDE.md").read_text(encoding="utf-8")
RULES = (ROOT / "claude/rules/claude-md.md").read_text(encoding="utf-8")
TEMPLATE = re.search(r"```markdown\n(.*?)```", RULES, re.S).group(1)
SAMPLE = TEMPLATE.replace(
    "<リポジトリを一言で説明する句>",
    "社員のPCはこのシステムだけで仕事が済み、AIが進め、人は確かめてうなずくだけで案件が終わる。",
) + """
原則がぶつかったときは、番号の小さい方を先にする。

# 原則1: 安全

## 目的: 本番と、ほかの人の作業を壊さない

- 本番に影響する操作の前に、利用者に確かめる。
"""
QUESTIONS = """次の5つに、渡した文だけを読んで、それぞれ2文以内で答えてください。道具は使わず、推測なら推測と書いてください。
1. 命題・原則・目的・規則は、互いにどういう関係ですか。どの文からそう言えますか。
2. 段に分けて書いている意図は何ですか。どの文からそう言えますか。
3. 安全の原則は、どの命題から導かれていますか。どの文からそう言えますか。
4. 安全・人間側の最適化・AI 側の最適化のほかの原則は、何から導きますか。どの文からそう言えますか。
5. 規則に無い場面では、何をもとに動きますか。どの文からそう言えますか。
"""
CASES = {
    "全体の CLAUDE.md だけ(R1-1)": GLOBAL,
    "リポジトリの CLAUDE.md だけ(R3-2・R5-2)": SAMPLE,
    "全体とリポジトリ(R3-1)": f"<全体のCLAUDE.md>\n{GLOBAL}\n</全体のCLAUDE.md>\n"
    f"<リポジトリのCLAUDE.md>\n{SAMPLE}\n</リポジトリのCLAUDE.md>",
}


def run(job):
    name, n = job
    env = dict(os.environ, CLAUDE_CODE_DISABLE_CLAUDE_MDS="1")
    args = [shutil.which("claude"), "-p", "--model", "claude-opus-5-5", "--setting-sources", "",
            "--disable-slash-commands", "--tools", "", "--no-session-persistence"]
    with tempfile.TemporaryDirectory() as folder:
        done = subprocess.run(args, cwd=folder, env=env, input=CASES[name] + "\n\n" + QUESTIONS,
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
    return name, n, done.returncode, done.stdout or done.stderr


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    jobs = [(name, n) for name in CASES for n in (1, 2, 3)]
    with ThreadPoolExecutor(6) as pool:
        for name, n, code, out in pool.map(run, jobs):
            print(f"## {name} 答え{n}(終了コード {code})\n{out.strip()}\n", flush=True)


if __name__ == "__main__":
    main()

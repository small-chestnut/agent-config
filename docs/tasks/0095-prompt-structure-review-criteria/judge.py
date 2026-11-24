"""決まりの文書の、上の段と下の段の組を、決まりの文書を読まない新しいセッションに採点させる(手順5)。

使い方: python judge.py <出力の JSON> <組の名前>=<git の ref か work> ...
例: python judge.py out.json before=3be2495 after=work
ref を渡すとその時点のファイルを、work を渡すと作業ツリーのファイルを読む。
組は、命題→原則・原則→目的・目的→目指す状態・(すぐ上の見出し)→規則。前後は混ぜて並べ、3回採点して多数決。
"""
import json, os, random, re, shutil, subprocess, sys, tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

QUESTION = """決まりの文書の、上の段の文(親)と、そのすぐ下の段の文(子)の組を並べます。ラベル(原則・目的・目指す状態)は段の名前で、評価しません。組ごとに2つを判定してください。
a. 言い換え: 親が、子を語尾や言い回しだけ変えて言い直したもので、子とは別のやり方では親を果たせない(y か n)
b. 判断できる: 親の文だけを読んで、子が親に合っているか合っていないかを、根拠を1文で言って決められる。親が短すぎる・広すぎる・関係が読めないなら n(y か n)
出力は、1行に1組ずつ「番号 a b」だけ(例「12 n y」)。前置きは書かない。

"""
PATHS = ["claude/CLAUDE.md", "claude/rules", "claude/skills", ".claude/skills/team-kanban-page"]
PROPOSITION = "AI 駆動開発の最適化(面は人間側の最適化と AI 側の最適化。安全は、最適化の制約条件。)"
LABEL = re.compile(r"^(原則[0-9]*|目的|目指す状態): ")


def files(ref):
    if ref == "work":
        names = subprocess.run(["git", "ls-files", *PATHS], capture_output=True, text=True, encoding="utf-8").stdout.split()
        return {n: open(n, encoding="utf-8").read() for n in names if n.endswith(".md")}
    names = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref, "--", *PATHS], capture_output=True, text=True, encoding="utf-8").stdout.split()
    return {n: subprocess.run(["git", "show", f"{ref}:{n}"], capture_output=True, text=True, encoding="utf-8").stdout
            for n in names if n.endswith(".md")}


def pairs(text):
    """(段の種類, 親, 子) の列。front matter とコードブロックの中は除く。"""
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    out, cur, fence = [], {}, False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        m = re.match(r"^(#{1,3}) (原則|目的|目指す状態)", s)
        if m:
            level = len(m.group(1))
            body = LABEL.sub("", re.sub(r"^#+ ", "", s))
            cur = {k: v for k, v in cur.items() if k < level}
            parent = cur[max(cur)] if cur else PROPOSITION
            kind = {1: "命題→原則", 2: "原則→目的", 3: "目的→目指す状態"}[level]
            out.append((kind, parent, body))
            cur[level] = body
        elif line.startswith("- ") and cur:
            out.append(("見出し→規則", cur[max(cur)], s[2:]))
    return out


def ask(text):
    env = dict(os.environ, CLAUDE_CODE_DISABLE_CLAUDE_MDS="1")
    claude = shutil.which("claude")
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        r = subprocess.run([claude, "-p", "--model", "claude-opus-5-5", "--setting-sources", "", "--disable-slash-commands",
                            "--tools", "", "--no-session-persistence"], cwd=d, env=env, input=text,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout if r.returncode == 0 else ""


def main(argv):
    out_path, specs = argv[0], [a.split("=", 1) for a in argv[1:]]
    items = []
    for name, ref in specs:
        for path, text in sorted(files(ref).items()):
            items += [(name, kind, path, parent, child) for kind, parent, child in pairs(text)]
    order = list(range(len(items)))
    random.Random(1).shuffle(order)
    chunks = [order[i:i + 45] for i in range(0, len(order), 45)]

    def judge(chunk):
        text = QUESTION + "\n\n".join(f"{n + 1}\n親: {items[n][3]}\n子: {items[n][4]}" for n in chunk)
        return {int(m.group(1)) - 1: (m.group(2), m.group(3)) for m in re.finditer(r"^(\d+) ([yn]) ([yn])", ask(text), re.M)}

    votes = defaultdict(list)
    for _ in range(3):
        with ThreadPoolExecutor(8) as pool:
            for got in pool.map(judge, chunks):
                for n, v in got.items():
                    votes[n].append(v)
    rows = []
    for n, (name, kind, path, parent, child) in enumerate(items):
        v = votes[n]
        rows.append(dict(name=name, kind=kind, path=path, parent=parent, child=child, votes=len(v),
                         restated=sum(x[0] == "y" for x in v) * 2 > len(v), unjudged=sum(x[1] == "n" for x in v) * 2 > len(v)))
    json.dump(rows, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    total = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        c = total[(r["name"], r["kind"])]
        c[0] += 1; c[1] += r["restated"]; c[2] += r["unjudged"]
    for k in sorted(total):
        print(*k, "組", total[k][0], "言い直し", total[k][1], "判断できない", total[k][2])
    print("票が3でない組", sum(r["votes"] != 3 for r in rows))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1:])

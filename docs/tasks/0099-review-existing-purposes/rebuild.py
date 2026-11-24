"""plan.txt のとおりに、決まりの文書の目的と規則を置き直す。組み直す前の文書は、コミット BASE のもの。

使い方(リポジトリのルートで): python docs/tasks/0099-review-existing-purposes/rebuild.py <書き出すフォルダ(リポジトリのルートなら .)>
plan.txt の行: 「@ 」文書 / 「P 」原則 / 「H 」目的(「H =」は前の見出しのまま) / 「+ 」足す規則 / 「~ <番号> 」文を直す規則 / 数字は前の文書の規則の番号。
前の規則は、どれも1回だけ置かれていなければ止まる。
"""
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from blocks import docs, split

BASE = "dc598d0"
PRI = {
    "S": "安全 ― AI の操作で、利用者が取り返しのつかない損失を負わない",
    "U": "人間側の最適化 ― 利用者が、AI の出力と作業の今を、少ない負担で正確につかみ、自分の意図どおりに AI を動かせる",
    "A": "AI 側の最適化 ― Claude が、どのリポジトリでも、要るものだけを読み、手戻りなく、作業を終えられる",
}
out = Path(sys.argv[1])
sec = {}
for l in (Path(__file__).parent / "plan.txt").read_text(encoding="utf-8").splitlines():
    if l.startswith("@ "):
        cur = sec.setdefault(l[2:], [])
    elif l.strip():
        cur.append(l)
assert set(sec) == {p.as_posix() for p in docs(".")}, "plan.txt の文書と、リポジトリの文書が違う"


def before(rel):
    done = subprocess.run(["git", "show", f"{BASE}:{rel}"], capture_output=True, check=True)
    return done.stdout.decode("utf-8").replace("\r\n", "\n")


count = {"目的": 0, "足した規則": 0, "直した規則": 0}
for rel, lines in sec.items():
    head, pre, items = split(before(rel))
    blocks = [t for k, t in items if k == "B"]
    heads = [t.removeprefix("## 目的: ") for k, t in items if k == "H"]
    used, body, principles, pos = [], [], 0, 0
    for l in lines:
        if l.startswith("P "):
            principles += 1
            body.append(("P", f"# 原則{principles}: {PRI[l[2:]]}"))
        elif l.startswith("H "):
            text = l[2:]
            if text.startswith("="):
                found = [h for h in heads if h.startswith(text[1:])] if text != "=" else [heads[pos]]
                assert len(found) == 1, (rel, l)
                text = found[0]
                pos = heads.index(text)
            pos += 1
            count["目的"] += 1
            body.append(("H", "## 目的: " + text))
        elif l.startswith("+ "):
            count["足した規則"] += 1
            body.append(("B", "- " + l[2:]))
        elif l.startswith("~ "):
            n, text = l[2:].split(" ", 1)
            count["直した規則"] += 1
            used.append(int(n))
            old = blocks[int(n) - 1]
            body.append(("B", "- " + text + old[len(old.split("\n")[0]):]))
        else:
            for part in l.split(","):
                a, _, b = part.partition("-")
                for n in range(int(a), int(b or a) + 1):
                    used.append(n)
                    body.append(("B", blocks[n - 1]))
    assert sorted(used) == list(range(1, len(blocks) + 1)), (rel, sorted(used))
    if principles > 1 and "番号の小さい方" not in pre:
        pre = "\n原則がぶつかったときは、番号の小さい方を先にする。"
    text = head + pre.rstrip("\n") + ("\n" if pre.strip() else "")
    last = ("", "")
    for kind, t in body:
        if kind in "PH" or last[0] in ("P", "H") or "\n" in last[1]:
            text += "\n"
        text += t + "\n"
        last = (kind, t)
    path = out / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
print(count)

"""決まりの文書を、前文・原則の見出し・目的の見出し・規則のかたまりに分ける。"""
import re
from pathlib import Path


def docs(root):
    root = Path(root)
    return [root / "claude/CLAUDE.md", *sorted((root / "claude/rules").glob("*.md")),
            *sorted((root / "claude/skills").glob("*/SKILL.md")), *sorted((root / ".claude/skills").glob("*/SKILL.md"))]


def split(text):
    """(--- で囲んだ所, 最初の見出しの前の文, [(種類, 文)])。種類は P(原則)・H(目的)・B(規則1つと、続く表・コードブロック・下の段の箇条書き)。"""
    head, body = "", text
    m = re.match(r"---\n.*?\n---\n", text, re.S)
    if m:
        head, body = m[0], text[m.end():]
    out, pre, fence, cur = [], [], None, None
    for l in body.splitlines():
        f = re.match(r"(`{3,})", l)
        if f and fence is None:
            fence = f[1]
        elif f and l.strip() == fence:
            fence = None
            cur.append(l)
            continue
        if fence is None and l.startswith("# 原則"):
            out.append(["P", [l]])
            cur = None
        elif fence is None and l.startswith("## 目的"):
            out.append(["H", [l]])
            cur = None
        elif not out:
            pre.append(l)
        elif fence is None and (l.startswith("- ") or (cur is None and l.strip())):
            cur = [l]
            out.append(["B", cur])
        elif cur is not None:
            cur.append(l)
    return head, "\n".join(pre), [(k, "\n".join(v).rstrip()) for k, v in out]

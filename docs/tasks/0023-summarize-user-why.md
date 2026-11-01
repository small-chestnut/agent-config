ステータス: 実装レビュー中

# ゴール

壁打ちの後で PL が SE に渡すタスクの文の中の、利用者の「なぜ」は、利用者の言葉のままではなく、利用者が言った内容だけを PL がまとめた文になっている。利用者は、タスクを始めるときの PL の報告で、まとめた「なぜ」を見られる。

範囲外: PL の答えの渡し方を変えること、グローバルの CLAUDE.md の「なぜ」を残す規則を変えること、SE・PG・QA の skill を変えること。

# 受け入れ条件

1. skill `task-team-lead` に「まとめの中の利用者の「なぜ」は、利用者が言った内容だけを PL がまとめた文。」の行があり、「まとめの中の利用者の「なぜ」は、利用者の言葉のまま引く。」の行が無い。
2. skill `task-team-lead` に「タスクを始めるとき、まとめた「なぜ」を利用者に伝えている。」の行が、1 の行の次にある。
3. `claude/skills/task-team-lead/CLAUDE.md` に、見出し「目指す状態: SE に届く利用者の「なぜ」は、利用者の言葉ではなく、利用者が一番やりたいこと」と、その下の「利用者の「なぜ」を、言葉のまま引く形に戻していない。」の行がある。
4. skill `task-team-lead` と `claude/skills/task-team-lead/CLAUDE.md` の、1〜3 のほかの行は、変える前と同じである。
5. `python -m unittest discover -s tests` が全部通る。

# 設計

書き換える `claude/skills/task-team-lead/SKILL.md` の42行目にも、その見出し(原則1「受け渡しの記録が、タスクごとに1つのファイルにある」)にも、ADR の番号は無い。この SKILL.md がモジュール `task-team-lead` の仕様なので、仕様はこの SKILL.md を直す。新しい名前は無い。

「言った内容だけ」なので、PL の理由はまとめに入らない。壁打ちの途中で訂正・撤回した認識は、41行目「まとめには、利用者が訂正・撤回した認識を入れない。」が除く。

利用者の「なぜ」(「わたしの言葉」が「わたしが一番やりたいこと」かは怪しい)は、後で同じ機能を変えるときにも守る理由なので、`claude/skills/task-team-lead/CLAUDE.md` に置く。タスクを始めるときに見せる行の理由は PL の答えから来たもので、利用者の「なぜ」ではないので、CLAUDE.md には置かない。

## 手順

1. PG: `claude/skills/task-team-lead/SKILL.md` を、次の表のとおりに直す。表の行番号は main の SKILL.md のもの。表に無い行は変えない。

   | 場所 | 変える前 | 変えた後 |
   |---|---|---|
   | 42行目 | `- まとめの中の利用者の「なぜ」は、利用者の言葉のまま引く。` | `- まとめの中の利用者の「なぜ」は、利用者が言った内容だけを PL がまとめた文。` |
   | 42行目の次に足す | — | `- タスクを始めるとき、まとめた「なぜ」を利用者に伝えている。` |

2. PG: `claude/skills/task-team-lead/CLAUDE.md` の23行目(`- SE には、利用者が聞いた PL の答えが、言葉のまま届いている。`)の後に、空行を1つ挟んで次の3行を足す。ほかの行は変えない。

   ```
   ### 目指す状態: SE に届く利用者の「なぜ」は、利用者の言葉ではなく、利用者が一番やりたいこと

   - 利用者の「なぜ」を、言葉のまま引く形に戻していない。
   ```

3. PG: コミットメッセージの本文に、利用者の「なぜ」を書く: 「利用者の言葉が、利用者が一番やりたいことと同じとは限らない。」
4. PG: `python -m unittest discover -s tests` を流し、結果を「実装」の節に書く。

## テスト一覧

文書だけの変更なので、テストは作らない。

| 確かめ方 | 受け入れ条件 |
|---|---|
| `git diff main -- claude/skills/task-team-lead/SKILL.md` が、手順1 の表の2か所だけ | 1・2・4 |
| `git diff main -- claude/skills/task-team-lead/CLAUDE.md` が、手順2 の3行の追加だけ | 3・4 |
| `python -m unittest discover -s tests` の結果(足した行の字数は `tests/test_skill_md_bullet_length.py` が見る) | 5 |

# 実装

設計どおりに、SKILL.md の2か所と CLAUDE.md の3行を直した。足した行は設計が字句まで決めているので、削れる語は無いと見て変えていない。

- `git diff main -- claude/skills/task-team-lead/SKILL.md`: 42行目の置き換えと、次の行の追加だけ。
- `git diff main -- claude/skills/task-team-lead/CLAUDE.md`: 見出し1行・空行・規則1行の追加だけ。
- `python -m unittest discover -s tests`: 64 件、全部通った。lint のコマンドは CLAUDE.md に無い。

# レビュー

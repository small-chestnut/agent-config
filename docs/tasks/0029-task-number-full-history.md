ステータス: 実装中

# ゴール

skill `task-team-lead` で PL がタスクの番号を決めるために main の履歴から記録の名前を引くコマンドが、作業ブランチで足して消してから `--no-ff` でマージした記録の名前も返し、最大の番号を正しく引ける。

今のコマンド `git log main --format= --name-only -- <記録を置くフォルダ>` は、git の履歴の簡略化(history simplification)で、記録を足して消した作業ブランチを飛ばす。マージの結果では記録が消えているので、マージのコミットは第1親(main)とそのフォルダで同じになり、git は第1親だけをたどる。`--full-history` を付けると簡略化をせず、作業ブランチのコミットも返す。

範囲外: squash マージ・rebase マージで作業ブランチのコミットが main の履歴に残らない場合。

# 受け入れ条件

main(958051b)からの差分で言う。

1. `claude/skills/task-team-lead/SKILL.md` の 33 行目が、「- main の履歴にある記録の名前は、`git log main --full-history --format= --name-only -- <記録を置くフォルダ>` で引いている。」である。
2. 1 のほかの行は、main と同じである。
3. 1 の行のコマンドの `main` を `958051b`、`<記録を置くフォルダ>` を `docs/tasks` にして走らせると、`docs/tasks/0027` で始まる名前を返し、それより大きい番号の名前を返さない。
4. 1 の行は 60 字以内(`claude/hooks/check_rule_length.py` の数え方)。
5. `python -m unittest discover -s tests` が全部通る。

# 設計

決まりの文書だけの変更。`SKILL.md` は決まりの文書そのものが仕様なので、`docs/specs/` は作らない。仕様で変える行は受け入れ条件1。

書き換える行(33 行目)とその見出し「受け渡しの記録が、タスクごとに1か所にある」に、ADR の番号は付いていない。読む ADR は無く、ADR も提案しない。

出典: git log の「History Simplification」(https://git-scm.com/docs/git-log#_history_simplification)。既定の簡略化は、マージのコミットがある親とパスで同じ(TREESAME)なら、その親だけをたどる。`--full-history` は親を刈らない。

## 手順

| 番号 | する人 | すること |
|---|---|---|
| 1 | PG | `claude/skills/task-team-lead/SKILL.md` の 33 行目のコマンドの `git log main` の後に ` --full-history` を足し、受け入れ条件1の行にする |
| 2 | PG | 確かめ: 下の「テスト一覧」の確かめ方を全部走らせる |
| 3 | PG | コミットする。本文に理由を書く: 記録を作業ブランチで足して消してから `--no-ff` でマージするので、既定の履歴の簡略化がそのブランチを飛ばし、0027 まであるのに 0022 までしか返さなかった |
| 4 | PL | main にマージし、push し、agent-config の main のチェックアウトで `install.ps1 -Yes` を走らせる。`~/.claude/skills/task-team-lead/SKILL.md` の行に `--full-history` があるのを確かめる |

## テスト一覧

文書だけの変更なので、テストは作らない。確かめ方を並べる。

| 確かめ方 | 受け入れ条件 |
|---|---|
| `git diff 958051b -- claude/skills/task-team-lead/SKILL.md` が、33 行目の1行の置き換えだけ | 1・2 |
| `git diff 958051b --stat` が、`claude/skills/task-team-lead/SKILL.md` と `docs/tasks/0029-task-number-full-history.md` だけ | 2 |
| `git log 958051b --full-history --format= --name-only -- docs/tasks \| grep -oE 'docs/tasks/[0-9]{4}' \| sort -u \| tail -1` が `docs/tasks/0027` | 3 |
| `python -m unittest discover -s tests`(`test_skill_md_bullet_length` が 1 の行の字数を数える) | 4・5 |

# 実装

# レビュー

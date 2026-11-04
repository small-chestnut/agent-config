ステータス: 実装レビュー済み

# 進み具合

- 利用者待ち: なし
- [x] 1. やり方を決める(済んだ印: 受け入れ条件 4 件・ADR の案 0 件)
- [x] 2. 全体の CLAUDE.md から本番の1行を消し、「なぜ」を残す(前: 1)(済んだ印: 受け入れ条件 1・3 を満たし、2 は記録の本文を除いて 0 件)
- [x] 3. テストを流す(前: 2)(済んだ印: 64 件が全部 OK・受け入れ条件 4 を満たした)
- [x] 4. できたものを見直す(前: 3)(済んだ印: レビューの節に実装レビューの結果がある・指摘 0 件)

# ゴール

利用者が本番の DB を直すよう頼んだとき、AI が全体の CLAUDE.md の規則を理由に「そちらでやってください」と返さない。そのために、`claude/CLAUDE.md` の原則1 から「本番環境の接続情報・認証情報に触れる作業は、利用者がしている。」の1行を消し、利用者の「なぜ」を `.claude/rules/global-claude-md.md` に残す。

範囲外: permissions・フック・サンドボックス(`claude/user-settings.json` の ask の `execute_plan` を含む)。`claude/CLAUDE.md` のほかの行。task-team の skill の「本番環境に触る作業」の行。main へのマージ・push・`install.ps1 -Yes`(PL がする)。

# 受け入れ条件

4d26cb7 からの差分で言う。

1. `claude/CLAUDE.md` の差分は、「- 本番環境の接続情報・認証情報に触れる作業は、利用者がしている。」の1行を消しただけ。
2. `git grep 接続情報・認証情報` が 0 件。
3. `.claude/rules/global-claude-md.md` の原則1 の、目指す状態「この文書は、deny に届く前に安全な行動を選ばせる文だけを持つ」とその下の2行の次に、次の目指す状態と1行がある。ほかの行は変わっていない。
   ```
   ### 目指す状態: この文書は、利用者が頼んだ本番の作業を断らせる文を持たない

   - 利用者は、本番の DB を直すよう頼んでも、この文書の1行を理由に断られ、イライラしていた。
   ```
4. リポジトリのルートで `python -m unittest discover -s tests` が全部 OK。

# 設計

## 書き換える所と ADR

- `claude/CLAUDE.md` 25行目。その行にも、見出し「本番環境と安全設定は、自分の判断では変えない」にも ADR の番号は無い。読む ADR は無い。
- `.claude/rules/global-claude-md.md` の原則1。ADR の番号は無い。
- ADR は書かない。この1行を消すのは、`.claude/rules/global-claude-md.md` の「止めなければならない操作は、deny とフックが止めている。」に沿う変更で、新しい決定ではない。

## 消しても残る守り(確かめた事実)

- LogiFee の本番に書く `mcp__logifee-nnm__execute_plan`・`mcp__logifee-sd__execute_plan` は、`claude/user-settings.json` の `ask` にある(66・67行目)。
- 「破壊的な DB 操作(DROP / TRUNCATE / WHERE なし DELETE)は、ローカル・開発用の DB にだけしている。」は `claude/CLAUDE.md` に残る。
- パスワード・API キー・トークンを入力欄に打ち込まないのは、Claude Code のシステムプロンプトの決まり(この会話のシステムプロンプトの「Prohibited」で確かめた)。

## 手順(する人: どれも PG)

1. `claude/CLAUDE.md` から、受け入れ条件 1 の1行を消す。見出しと前後の行はそのまま。
2. `.claude/rules/global-claude-md.md` に、受け入れ条件 3 の目指す状態と1行を足す。目指す状態の前後には空の行を1つずつ。
3. `python -m unittest discover -s tests` を流す。
4. 1・2 を1つのコミットにする。本文に利用者の「なぜ」(本番の DB を直すよう頼んでも、この1行を理由に断られ、イライラしていた)を書く。

## テスト一覧

文書だけの変更なので、テストは作らない。

| 確かめ方 | 大きさ | 受け入れ条件 |
|---|---|---|
| `git diff 4d26cb7 -- claude/CLAUDE.md` が、消した1行だけ | ― | 1 |
| `git grep 接続情報・認証情報` が 0 件 | ― | 2 |
| `git diff 4d26cb7 -- .claude/rules/global-claude-md.md` が、足した目指す状態と1行(と空の行)だけ | ― | 3 |
| `python -m unittest discover -s tests` が全部 OK | ― | 4 |

## 作業の前提

# 実装

- `claude/CLAUDE.md` の1行を消し、`.claude/rules/global-claude-md.md` に目指す状態と1行を足した(`git diff` で、その差分だけ)。
- `git grep 接続情報・認証情報` は、この記録(ゴールと受け入れ条件の引用)の4行だけに残る。`claude/` とルールには 0 件。記録を消せば 0 件になる。
- `python -m unittest discover -s tests`: 64 件、OK。lint のコマンドは無い。

# レビュー

指摘なし

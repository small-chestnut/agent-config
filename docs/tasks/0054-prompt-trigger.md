# 0054-prompt-trigger

ステータス: 実装中

## 進捗

- 利用者待ち: なし
- [x] 1. やり方を決める(完了条件: 設計の節をコミットした)
- [ ] 2. skill `prompt-structure` の、いつ使うかの説明(description)を書き換える(依存: 1)(完了条件: `claude/skills/prompt-structure/SKILL.md` の 3 行目が受け入れ条件 1 の行と一致する)
- [ ] 3. できたものを見直す(依存: 2)(完了条件: レビューの節に QA の結果が1件ある)

## ゴール

規則を足す・消す・直す案を出す場面(会話の返答・タスクの文・設計の中)でも、AI が案を書く前に skill `prompt-structure` を読み込む。そのために、その skill の description(AI が読み込むかを決めるときに見る、いつ使うかの説明)に、その場面を先頭に書く。規則の数は増やさない。

なぜ: 規則の案を、`prompt-structure` を読み込まずに書いたため、その skill に既にある規則を破った案が利用者に出た。利用者は、AI がプロンプトエンジニアリングを怠るのを見張って直す役を負いたくない。規則は既にあるので、規則をもう1行足しても直らない。読み込まれる場面の方を直す。

範囲外: `prompt-structure` の本文(原則・目的・目指す状態・規則)と、ほかの skill・全体の CLAUDE.md・hooks・settings の書き換え。

## 受け入れ条件

1. `claude/skills/prompt-structure/SKILL.md` の description の行が、次の1行である。

   ```
   description: 規則を足す・消す・直す案を出すとき(会話・タスクの文・設計の中も)と、CLAUDE.md・skill・ほかの AI への指示(プロンプト)を書く・直すときに、案や文を書く前に読む型。原則・目的・目指す状態・規則の4段の入れ子で書く。
   ```

2. description の行に、利用者の発言や返す文の言い回し(文例)が無い。
3. description の行のほかは、`claude/skills/prompt-structure/SKILL.md` が変わっておらず、ほかの文書も、このチケットのほかは変わっていない。規則の行の数は変わらない。
4. `python -m unittest discover -s tests` が 71 件とも通る。

## 設計

### 書き換える行と、付いた ADR

| ファイル | 書き換える所 | 付いた ADR |
|---|---|---|
| `claude/skills/prompt-structure/SKILL.md` | 3 行目(frontmatter の `description:`) | なし |

description の行と frontmatter には ADR の番号が無いので、読む ADR は無い。後から変えにくい決定ではないので、ADR は作らない。skill の SKILL.md はその文書が仕様なので、`docs/specs/` に仕様は作らない。

### 直し方の決め方

- Claude Code は、どの skill も description だけを常に読み、その説明に合う場面で skill の本文を読み込む。今の description は「書く・直すとき、規則を足す・消すとき」で、規則を変える案を出す場面が書かれておらず、先頭は書く・直す場面になっている。
- 公式の文書は、いちばん大事な使う場面を description の先頭に置き、使う場面を表す言葉を入れるよう勧めている。そこで、読み込まれなかった場面(案を出すとき)を先頭に置き、会話・タスクの文・設計の中も含むと書く。読む時を「案や文を書く前」と書く。
- 別の欄 `when_to_use` は足さない。description 1行で足り、欄を増やすと置き場が2つになる。
- 本文の規則は変えない。案を書く前に読み込まれれば、既にある規則(状態だけでは守れなかった所にだけ規則を置く・プロンプトは一般の文だけで書く)が効く。
- 出典: Claude Code の skill の文書 <https://code.claude.com/docs/en/skills>(frontmatter の表の `description` と `when_to_use` の行、Troubleshooting の「Skill not triggering」)。

### description を書き換える(する人: PG)

`claude/skills/prompt-structure/SKILL.md` の 3 行目を、受け入れ条件 1 の行に置き換える。ほかの行は変えない。

コミットメッセージの本文には、ゴールの「なぜ」をまとめて書く。

### テスト一覧

文書だけの変更なので、テストは作らない。skill が読み込まれるかは AI がその場で決めることで、このリポジトリのテストでは確かめられないので、確かめるのは書いた文だけ。

| 確かめ方 | 大きさ | 受け入れ条件 |
|---|---|---|
| `sed -n 3p claude/skills/prompt-structure/SKILL.md` が受け入れ条件 1 の行と一字も違わない | — | 1 |
| 書き換えた行を読み、発言や返す文の例が無い | — | 2 |
| `git diff main --stat` が `claude/skills/prompt-structure/SKILL.md` とこのチケットだけで、SKILL.md の差分が 3 行目の置き換えだけ | — | 3 |
| `python -m unittest discover -s tests` が 71 件 OK | 小 | 4 |

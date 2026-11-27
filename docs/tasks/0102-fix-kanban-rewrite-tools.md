# 0102-fix-kanban-rewrite-tools

ステータス: 取りやめ
PC: Reo-Desktop

## 進捗

- 利用者待ち: なし
- [x] 1. やり方を決める(完了条件: サブエージェントが今の道具で書き直せない段と、直し方を利用者が決めている)

## 難しさ

- SE: 中(道具で何ができるかを確かめ、手順の行を道具の呼び出しに合わせる)

## ゴール

skill `team-kanban` の書き直し方を、PL が頼むサブエージェントが今の道具で実行でき、かんばんのカードが書き直せるようにする。

範囲外: かんばんのページ(`team-kanban-page`)の見た目と動き。

起きていること(gemini の PL からの知らせ、2026-11-26、利用者の「頼んで」による): かんばんの書き直しを頼んだサブエージェントが3回とも、`datasets/cards` の `source` が指す `/_blob/…` の `cards.json` を読めず、新しいファイルをかんばんに上げる道具も無いと返した。SKILL.md の「新しいファイルをかんばんにアップロードする」「`source.url` を新しいファイルに替え、古いファイルを消す」が、今の道具(ArtifactData の読み書き・Artifact の公開ファイルの読み書き)で実行できない。

SE が確かめたこと(2026-11-27、Reo-Desktop): 読むだけを頼んだ `model: "sonnet"` のサブエージェントは、Artifact と ArtifactData を ToolSearch で読み込み、`cards.json` を Artifact の `read` に `path`(`_blob/` の後の id)を付けて読めた。上げる(`publish` に `asset: true`)・消す(`delete` に `path`)のパラメータも見つけた。ただし、上げる・指し替える・消すまでは試していない。PL と同じ頼み方で書き直しをさせたサブエージェントは、モデルの safeguards に止められ、途中で終わった(かんばんは変わっていない)。かんばんのアセットには、`source` が指していない古い `cards.json` が2つ残っている。

gemini の PL の答え(2026-11-27): 3回とも、task-team-lead のとおりの頼む文で、`subagent_type: "general-purpose"`・`model: "sonnet"`。同じ頼み方で 0109 のカードは前に書き直せた。1回目はチケットがまだ無かった。2・3回目はチケットがあり、「cards.json を読めず、アップロードする手段も無い」と返った。PL のセッションでは Artifact は読み込み済み、ArtifactData は deferred で、サブエージェントの側の道具は見えていない。PL 自身は `Artifact` の list を scope `files` で引き、cards.json が無いとしていた(cards.json は公開ファイルでなくアセットで、scope `assets` で出る)。

再現(2026-11-27、Reo-Desktop、agent-config の SE のセッションから): task-team-lead のとおりの頼む文(`general-purpose`・`sonnet`、チケットは 0102)で、サブエージェントは書き直せた。`datasets/cards` は version 762 になり、新しい cards.json は 411 行で、前の 410 行は1行も変わらず、0102 の行が1行増えた。指していた前のファイルは消え、それより古い2つは残っている。gemini の PL での失敗は、ここでは再現しなかった。

gemini の PL での4回目(2026-11-27、同じ頼む文): また「cards.json を読む手段と、アップロードする手段がこのセッションに無い」と返った(0111 のチケットは片付けた後で、無かった)。

原因(2026-11-27、gemini の PL のサブエージェントに読むだけの調べをさせて分かった): gemini の PL のセッション(2026-11-26 に始まった)の Artifact の道具には、アセットを読む・上げる・消すパラメータが無く、`read` に id を渡すと「this session cannot read an artifact's asset store — pass a file's published path」と断られる。ArtifactData は ToolSearch で読み込めて、`datasets/cards` を読めた。Artifact の道具でアセットを扱えるかはセッションごとに違い、SKILL.md の書き方では直らない。

## 要件

### 分けたタスク

### 決まっていない問い


## 設計

### ADR

- 0102-1(却下): カードのデータを保存した行に移さず、gemini の PL のセッションを始め直すだけにする。

### 置くファイルと名前・データ

### 手順

### テスト一覧

| テスト名 | テストサイズ | 受け入れ条件 |
|---|---|---|

### サブタスクの前提

## 実装

## レビュー

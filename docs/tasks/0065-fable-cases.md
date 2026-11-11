# 0065-fable-cases

ステータス: 壁打ち中
PC: Reo-Desktop

## 進捗

- 利用者待ち: Fable の場合を用意したい「なぜ」の答え(サイドバーの PL の下の、0065-fable-cases の SE の会話)
- [ ] 1. やり方を決める(完了条件: 設計の節に、Fable にする場合を決めた箇条の文がある)

## 難しさ

- SE: 高(Fable にする場合は、今の skill にも ADR 0059-1 にも無く、割り当ての枠そのものを決める)

## ゴール

task-team で、役割の仕事を Fable にする場合を決めて、skill に書く。

範囲外: 低・中・高の3段の割り当てそのものの見直し。Haiku を割り当てに入れること。

## 壁打ち

### 固まった要件

- Fable にすべき場合のパターンを用意する。(利用者のタスクの文)

### なぜ

- (まだ聞いていない)

### 分かっていること

- セッションは、自分のモデルと effort を替えられない。`set_session_model` と `set_session_effort` は、自分のセッションを対象にすると断る(道具の説明)。SE の難しさが高なら PL が SE の effort を high にし、PG と QA は SE が替える(task-team-se・task-team-lead の SKILL.md)。
- SE は、PG と QA を Fable にも替えられる。今より高いモデルに替えるときは、アプリが利用者に確かめる(bypass permissions のときは確かめない)(道具の説明)。
- Anthropic のページで Fable 5.2 を勧めるのは、難しい推論と長いエージェントの作業、1つのコンテキストに収まらない大きな作業、Opus 5.5 の高い effort でも足りないとき(https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence.md 。2026-11-11 に読んだ)。
- 同じページで、コードの課題(SWE-bench Pro)は、Fable 5.2 の high が解けた1件あたり $1.39 で 96.3%、Opus 5.5 の xhigh が $0.75 で 96.5%。調べもの(DeepResearch Bench II)では、Fable 5.2 は Opus 5.5 より費用 2.9 倍で 1.9 ポイント下。
- 利用者のプラン(Max)には、全部のモデルの週の枠とは別に、Fable の週の枠がある。2026-11-11 に `get_usage` で引いた値は、全部のモデル 40%、Fable 12%。Fable を使った分が全部のモデルの枠にも数えられるかは、引いた値からは分からない。
- モデルを会話の途中で替えるとキャッシュが効かない(ADR 0059-1 の理由6)。SE を Fable にすると、会話の途中で替えることになる。

### 決まっていない問い

- Fable にする場合を用意したいのは、Opus 5.5 の high で仕上がらなかった仕事があったからか、Fable の別の週の枠を使い切りたいからか。

## 受け入れ条件

## 設計

## 実装

## レビュー

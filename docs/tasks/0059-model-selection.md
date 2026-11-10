# 0059-model-selection

ステータス: 壁打ち中
PC: Reo-Desktop

## 進捗

- 利用者待ち: 設計に進めるかの答え([0059-model-selection SE](#local_2c6b7e42-4e16-429b-8b3e-11d051066959))
- [ ] 1. やり方を決める(完了条件: 設計の節がコミットされている)

## ゴール

チームの各役割(PL・SE・PG・QA)のモデルと effort を、役割に要る力で決める規則を作る。

タスクの文(利用者の言葉のまま): PLセッションが、単純なチーム管理の役割になった結果、必ずしもPLのモデル > SE/QA/PGのモデルという図式が成り立たなくなったように思う よって、モデル選定のルールを決めたい

範囲外: task-team の外(ふだんのセッション・サブエージェント一般)のモデル選びは決めない。

## 壁打ち

### 固まったこと

1. Fable を使う役割は SE と QA。
2. PL のモデルは Opus 5.5。
3. 子を PL より強いモデルにするときは、PL が起こした直後に `set_session_model` で上げる。
4. モデルと effort は、役割ごとに固定にせず、タスクで変える。なぜ: 性能は大事だが、利用者の財布(使用量の費用)も気にしたい。
5. 設計する SE 自身のモデルも、設計の難しさで変える。
6. 基準は、どの種類のタスクに、どのモデルのどの effort を割り当てるかの形で書く。基準の中身は SE が決める。なぜ: どのモデルがどの仕事に合うかは、利用者が決めても推測にしかならない。
7. 割り当ては、下の「割り当て」のとおり(SE が決めた)。

### 調べた事実

1. 今の規則は、`claude/skills/task-team-lead/SKILL.md` の「モデルと effort は、SE と QA が `claude-opus-5-5` の high、PG が `claude-sonnet-5-5` の medium。」と、`claude/skills/task-team-lead/CLAUDE.md` 原則3 の「PL は進捗管理だけで、Opus 級のモデルで足りる。」「子は起こした側のモデル以下しか選べず、PL のモデルが上限になる。」「Fable が要る設計は、利用者が SE のモデルを手で上げる。」。
2. 今の PL のセッションは `claude-fable-5-2` の high、この SE は `claude-opus-5-5` の high(2026-11-10 に `get_session` で引いた)。
3. 「起こした側のモデル以下」は、起こすときだけ正しい。`start_session` の `model` は「起こした側と同じ系統か安いもの。高いものは無視」。
4. 起こした後は、`set_session_model` と `set_session_effort` で、起こした側より高いモデル・effort に上げられる。高い方へ上げるときは、アプリが利用者に聞く。権限のモードが bypassPermissions なら聞かない(どちらも道具の説明による。まだ試していない)。
5. タスク 0056 で、タスクの中身の話は PL でなく SE の会話でする形になった(ADR 0056-1)。利用者が読む文の多くは、SE が書く。
6. 100万トークンあたりの値段(入力 / 出力)は、Fable 5.2 が $8 / $40、Opus 5.5 が $4 / $20、Sonnet 5.5 が $2 / $10、Haiku 5.5 が $0.10 / $0.50。Fable は Opus の2倍、Sonnet の4倍。
7. Anthropic の手引きでは、Fable 5.2 は「いちばん難しい推論と長い作業」向けで、effort は high から始める。high より上の伸びはまばらで、xhigh は測って伸びが出た所だけ。
8. 同じ手引きで、Opus 5.5 は medium で Opus 5 の high を越え(コードと知的作業)、effort は medium から始める。Sonnet 5.5 は、エージェントのコーディングで medium から始める。
9. 同じ手引きで、費用はトークン単価でなく、作業1つを終えるまでの合計で比べる。
10. モデルを替えると、その会話のキャッシュは使えず、次のターンで会話の全部を読み直す(キャッシュはモデルごと)。

出典(6〜10): Claude Code の skill `claude-api`(2026-11-03 時点の写し)の Current Models の表と、`shared/model-migration.md` の Fable 5.2・Opus 5.5・Sonnet 5.5 の「Choosing an effort level」。

### 決まっていない問い

1. 設計に進めるか。

### 割り当て

| タスクの種類 | PL | SE | QA | PG |
|---|---|---|---|---|
| ふつうのタスク(起こすときの値) | Opus 5.5 medium | Opus 5.5 high | Opus 5.5 medium | Sonnet 5.5 medium |
| 大きな変更(ADR を出す・本番に触る) | Opus 5.5 medium | Fable 5.2 high | Fable 5.2 high | Sonnet 5.5 high |

- 起こした直後に、PL が `set_session_model`・`set_session_effort` で、子をふつうのタスクの値に替える(起こすときは PL の値までしか選べないため)。
- SE は、ADR を出すと決めたら、設計を書く前に PL に知らせ、PL が SE・QA・PG を大きな変更の値に替える。
- PL のモデルは利用者が選ぶ(セッションは自分のモデルを替えられない)。
- 確かめること: 子の知らせで始まった PL のターンから、`set_session_model` が通るか。

## 受け入れ条件

## 設計

## 実装

## レビュー

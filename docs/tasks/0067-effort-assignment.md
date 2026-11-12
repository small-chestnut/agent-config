# 0067-effort-assignment

ステータス: 設計レビュー済み
PC: Reo-Desktop

## 進捗

- 利用者待ち: なし
- [x] 1. やり方を決める(完了条件: 設計の節に、直す6つのファイルと、足す・直す・消す行が文のまま書いてある。ADR 2件を提案で書いた)
- [/] 2. やり方を見直す(依存: 1)(完了条件: レビューの節の設計への指摘を、どれも設計の節で直し、ADR 2件が採用になった)
- [ ] 3. SE が最初のターンから high で動く形にする(依存: 2)(完了条件: skill `task-team-se` と `task-team-lead` の SKILL.md に「ADR 0067-1」を含む行が合わせて4行あり、「SE の難しさが高なら」の行が0行)
- [ ] 4. Fable にする途中の印を、SE と QA が ADR の履歴で確かめる形にする(依存: 2)(完了条件: skill `task-team-se`・`task-team-qa`・`task-team-lead` の SKILL.md に「0067-2」を含む行と見出しが合わせて5つある)
- [ ] 5. できたものを見直す(依存: 3・4)(完了条件: レビューの節の実装の指摘が0件か、どれも直した)

## 難しさ

- SE: 高(難しさの割り当ての枠そのものを決め直す。今の skill の物差しで高。利用者が先に xhigh に上げた)
- PG: 低(足す・直す・消す行と置く所は、設計の節に文のまま書いてある)
- QA: 高(設計レビューで、ADR 2件の決定が、LogiFee の記録と Anthropic の測定と README の目的に合うかを見る。枠を決める仕事のレビュー)

## ゴール

チームの役割のモデルと effort を決める作りを、浅い判断の SE 本人が自分の難しさと Fable に替える時を決めない形にする。

範囲外: QA の設計レビューの仕方(設計の節に code-review を low でかける形)と、SE が新しい作りを設計する前に既にある機能と ADR を探す手順(どちらも R-0718 の誤りの原因の候補として PL に別に知らせる)。LogiFee の R-0718 の作業そのもの。

## 壁打ち

PL が聞かずに回すタスクなので、壁打ちはしない。

### 分かっていること

- R-0718 の誤り9件のうち、1(手段を聞き続けた)・3(既にある ADR に反した)・6(数える前に言い切った)・7(数だけで本番に書く許しを取ろうとした)・8(報告が長く話が混ざった)は、全体の CLAUDE.md に既にある規則を守れなかったもの。仕事の難しさ(仕様・設計・規則でどこまで決まっているか)によらず、利用者と話すどの SE の仕事でも起きる。(LogiFee の SE の記録 `logifee-r0718-report.md`。PL が共有ノートのフォルダに置いた)
- 9(Fable に替えるのが遅れた)は、5 で ADR-2871-4 を取り下げて ADR 0065-1 の印に当たっていたのに、利用者に聞かれるまで PL に知らせなかったもの。SE は最初に自分の難しさを「中」と決めていた。(同じ記録)
- 2(段階に合わない直し方)と 4(既にある機能 `create_pair` を調べなかった)は、QA の設計レビューも通した。QA は ADR の文の食い違いやテストの抜けはよく拾った。4 は、Fable に替えた直後に SE が仕様とコードを grep して見つけた。(同じ記録)
- QA の設計レビューは、設計の節に skill `code-review` を low で1回かける形(skill `task-team-qa`。利用者が、AI だけで最後まで流しきるために決めた形。コミット c8fa8b4)。R-0718 の QA の effort は記録に無い。
- `start_session` の effort は、起こす PL の effort までしか選べない。`set_session_effort` で替えた値は、次のターンから効く。(道具の説明)
- Anthropic の測定: Opus 5.5 の medium → high で SWE-bench Pro は 92.8% → 95.3%、1件 $0.21 → $0.29。欠陥を探す課題は 0.827 → 0.850。xhigh は high より SWE-bench Pro で約 1.4 ポイント上、費用 2.5 倍。調べものの課題で Fable 5.2 は low 54.5・high 57.7、Opus 5.5 の medium は 59.6。勧めは、Opus 5.5 の medium から始め、高い effort でも足りないときに Fable 5.2。(https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence.md 。2026-11-12 に読んだ)
- 利用者の Max プランは、2026-11-12 に `get_usage` で、全部のモデルの週の枠が 31%、Fable の週の枠が 7%(週の 38% が過ぎたところ)。

### 決まっていない問い

- なし。

## 受け入れ条件

- skill `task-team-se` で、SE の難しさは、いつも高。
- skill `task-team-se` に、SE が最初のターンで自分の難しさを決める行と、SE の難しさを返答に書く行と、高なら PL に知らせる行が無い。
- skill `task-team-lead` で、SE・QA・PG を起こす最初の prompt は、3つとも、役割の skill を読んでターンを待つ指示だけ。
- skill `task-team-lead` で、PL は SE を起こしたら、high に替えてから、依頼を送る。
- skill `task-team-lead` に、SE が難しさを高と知らせてきたら effort を替える行が無い。
- skill `task-team-se` で、SE はコミットするたびに、このタスクの ADR の `git log -p` で、Fable にする途中の印に当たるかを確かめる。
- skill `task-team-se` に、入れた決定を消すことと、同じ決まりを変えることの意味が1行ずつある。
- skill `task-team-qa` で、QA は設計レビューの前に、このタスクの ADR の `git log -p` で、SE の Fable の印を確かめ、当たれば PL に知らせる。
- skill `task-team-lead` で、PL は SE を Fable にすると届いたら、SE か QA のどちらからでも替える。
- 3つの skill のフォルダの CLAUDE.md に、変えた形の「なぜ」がある。
- どの SKILL.md と CLAUDE.md の箇条書きも60字以内。

## 設計

### 書き換える所と、付いた ADR

- `claude/skills/task-team-se/SKILL.md` の「目的: AI の費用対効果を最適化する」の3つの目指す状態。見出しに ADR 0059-1(難しさ・モデルと effort)と ADR 0065-1(Fable)。
- `claude/skills/task-team-lead/SKILL.md` の「目指す状態: チームは、タスクごとに SE・PG・QA の3セッション」(行に ADR 0024-1・0056-2・0059-1)と「目指す状態: ターンの受け渡しは、子セッションどうしが直接している」(行に ADR 0059-1・0065-1)。
- `claude/skills/task-team-qa/SKILL.md`。今は費用対効果の目的が無い。
- 3つの skill のフォルダの `CLAUDE.md`(「なぜ」)。
- 読んだ ADR: 0059-1・0065-1(書き換える所に付いた番号)。0024-1・0056-2 の行は、prompt を依頼に言い換えるだけで、決定は変えない。
- 仕様: skill はプロンプトなので、SKILL.md が仕様。`docs/specs/` は直さない。用語集の「難しさ」の意味は変えない(SE は物差しで測らず、いつも高に置く)。

### ADR

- `docs/adr/0067-1-se-always-opus-high.md`(提案): SE は、難しさを決めずに、最初のターンから Opus 5.5 の high で動かす。ADR 0059-1 の SE の割り当てだけを置き換えるので、0059-1 は「採用」のまま。0059-1 の決めたことは番号の無い1文なので、「置き換える: 」には番号でなく「0059-1 の SE の割り当て」と書いた。
- `docs/adr/0067-2-check-fable-signal-from-adr-history.md`(提案): Fable にする途中の印は、SE がコミットのたびに、QA が設計レビューの前に、ADR の git の履歴で確かめる。ADR 0065-1 に足す決定で、置き換えない。

### 手順(する人: すべて PG)

#### 3. SE が最初のターンから high で動く形にする

1. `claude/skills/task-team-se/SKILL.md` の「- SE の難しさは、最初のターンで、中か高に決めている。」を、次の行に替える。

```
- SE の難しさは、いつも高。(ADR 0067-1)
```

2. 同じファイルの「- SE の難しさと理由は、最初のターンの返答にも書いている。」の行を消す。
3. 同じファイルの「- SE の難しさが高なら、最初のターンで PL に知らせている。」の行を消す。
4. `claude/skills/task-team-lead/SKILL.md` の次の2行を、

```
- SE への prompt は、`task-team-se` に従う指示と、タスクの文と、チケットの置き場。(ADR 0024-1)
- 聞かずに回すタスクは、SE への prompt にそう添えている。(ADR 0056-2)
- QA と PG への最初の prompt は、役割の skill を読んでターンを待つ指示だけ。
```

次の3行に替える。

```
- 最初の prompt は、3つとも、役割の skill を読んでターンを待つ指示だけ。(ADR 0067-1)
- SE への依頼は、`task-team-se` に従う指示と、タスクの文と、チケットの置き場。(ADR 0024-1)
- 聞かずに回すタスクは、SE への依頼にそう添えている。(ADR 0056-2)
```

5. 同じファイルの「- 3つを起こしたら、3つのセッションの id を、各子セッションに `SendMessage` で渡している。」の次に、次の行を足す。

```
- SE を起こしたら、`set_session_effort` で high に替えてから、依頼を `SendMessage` で送る。(ADR 0067-1)
```

6. 同じファイルの「- SE が難しさを高と知らせてきたら、SE の effort を high に替えている。(ADR 0059-1)」の行を消す。
7. 同じファイルの「- 替えるのは、`set_session_model` と `set_session_effort`。(ADR 0059-1・0065-1)」を、次の行に替える。

```
- 替えるのは、`set_session_model` と `set_session_effort`。(ADR 0059-1・0065-1・0067-1)
```

8. `claude/skills/task-team-se/CLAUDE.md` の「- 難しさを決めるのは、仕事の中身を読む SE にしている。」の次に、次の3行を足す。

```
- SE の誤りは、難しさによらず、利用者と話す規則(聞くこと・確かめること・報告の形)で起きる。
- 決まり方の物差しでは、その誤りを見込めないので、SE は難しさを決めずに high にしている。
- medium の本人が自分の難しさを決めると、浅い判断のまま上がらない。
```

9. `claude/skills/task-team-lead/CLAUDE.md` の「- セッションは、自分のモデルと effort を替えられない。SE のモデルと effort は、PL が替える。」の次に、次の行を足す。

```
- 起こすときの effort は、PL の effort を越えられない。SE は、起こしてから high に替える。
```

#### 4. Fable にする途中の印を、SE と QA が ADR の履歴で確かめる形にする

1. `claude/skills/task-team-se/SKILL.md` の「- 同じタスクで入れた決定を消すか、同じ決まりを3回変えたら、Fable と決めている。」の次に、次の3行を足す。

```
- 入れた決定を消すとは、このタスクで出した ADR を、却下か置き換え済みにするか、消すこと。(ADR 0067-2)
- 同じ決まりを変えるとは、このタスクの ADR の決めたことを書き換えるか、置き換えること。(ADR 0067-2)
- コミットするたびに、このタスクの ADR の `git log -p` で、この2つに当たるかを確かめている。(ADR 0067-2)
```

2. `claude/skills/task-team-qa/SKILL.md` の末尾に、空の行を1つ置いて、次の節を足す。

```
## 目的: AI の費用対効果を最適化する

### 目指す状態: SE の Fable の印は、SE が気づかなくても PL に届いている(ADR 0067-2)

- 設計レビューの前に、このタスクの ADR の `git log -p` で、SE の Fable の印を確かめている。
- 印は、skill `task-team-se` の、入れた決定を消すことと、同じ決まりを3回変えること。
- 印に当たっていたら、SE を Fable にするよう PL に知らせている。
```

3. `claude/skills/task-team-lead/SKILL.md` の「- SE が Fable と知らせてきたら、SE を `claude-fable-5-2` の high に替えている。(ADR 0065-1)」を、次の2行に替える。

```
- SE を Fable にする知らせは、SE か QA から届く。(ADR 0067-2)
- その知らせが届いたら、SE を `claude-fable-5-2` の high に替えている。(ADR 0065-1)
```

4. `claude/skills/task-team-lead/CLAUDE.md` の「- Fable にする仕事は SE が決め、ほかに要ると利用者が見た仕事は、利用者が手で上げる。」を、次の行に替える。

```
- Fable にする仕事は SE が決め、SE 自身の印は QA も確かめる。ほかは利用者が手で上げる。
```

5. `claude/skills/task-team-se/CLAUDE.md` の「- SE を途中で Fable にするのは、キャッシュを失うより、破綻の方が高くつくから。」の次に、次の行を足す。

```
- Fable の印は、気づきに頼らず、コミットのたびに ADR の履歴で確かめる形にしている。
```

6. `claude/skills/task-team-qa/CLAUDE.md` の末尾に、空の行を1つ置いて、次の節を足す。

```
## 目的: AI の費用対効果を最適化する

### 目指す状態: SE の Fable の印は、SE が気づかなくても PL に届いている

- SE が気づかなくても、別のセッションの QA が印を確かめ、PL に届く形にしている。
- 印が出る ADR は大きな変更にだけあり、大きな変更には設計レビューがある。
```

#### 終わったあと

- ADR 0067-1・0067-2 の状態は、設計レビューのあと QA か SE が「採用」にする。PG は直さない。
- main にマージしたあと、`install.ps1 -Yes` で入れる(PL)。

### テスト一覧

文書だけの変更なので、テストは作らない。確かめ方:

| 確かめ方 | 受け入れ条件 |
|---|---|
| `claude/skills/task-team-se/SKILL.md` を読み、「SE の難しさは、いつも高。(ADR 0067-1)」がある | SE の難しさは、いつも高 |
| 同じファイルを「最初のターンで、中か高」「最初のターンの返答にも」「SE の難しさが高なら」で検索し、0件 | SE が自分の難しさを決める行・返答に書く行・PL に知らせる行が無い |
| `claude/skills/task-team-lead/SKILL.md` を読み、「最初の prompt は、3つとも」の行と、「SE を起こしたら、`set_session_effort` で high に替えてから」の行がある | 最初の prompt・high に替えてから依頼 |
| 同じファイルを「難しさを高と知らせてきたら」で検索し、0件 | 高と知らせてきたら替える行が無い |
| `claude/skills/task-team-se/SKILL.md` に「(ADR 0067-2)」を含む行が3行ある | コミットのたびに確かめる・意味が1行ずつ |
| `claude/skills/task-team-qa/SKILL.md` を読み、「SE の Fable の印は、SE が気づかなくても PL に届いている(ADR 0067-2)」の見出しの下に3行ある | QA が設計レビューの前に確かめ、PL に知らせる |
| `claude/skills/task-team-lead/SKILL.md` を読み、「SE を Fable にする知らせは、SE か QA から届く。」の行と、「その知らせが届いたら」の行がある | どちらからでも替える |
| 3つの skill のフォルダの CLAUDE.md を読み、手順 3-8・3-9・4-4・4-5・4-6 の行がある | 「なぜ」がある |
| `python -m unittest discover -s tests` が通り、足した行を書いたとき字数のフック(check_rule_length.py)が何も知らせない | 60字以内 |

## 実装

## レビュー

### 設計レビュー

- 手順3-4 は71・72行目だけを「依頼」に言い換え、`task-team-lead/SKILL.md` の114行目と123行目の「SE への prompt に添える」が残る。新しい「最初の prompt は、3つとも、役割の skill を読んでターンを待つ指示だけ」とぶつかるので、2行も「SE への依頼」に直す手順が要る。
- 手順4-1 の「入れた決定を消すとは、このタスクで出した ADR を、却下か置き換え済みにするか、消すこと」は、設計レビューの指摘で提案中の ADR を却下にするふつうの流れ(`task-team-se/SKILL.md` の184行目)も印に当てる。ADR 0067-2 の理由と捨てた案も、提案のまま却下にする場合を分けていない。印に当てるかを決め、行と ADR に書く。

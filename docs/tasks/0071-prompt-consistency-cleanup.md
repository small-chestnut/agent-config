# 0071-prompt-consistency-cleanup

ステータス: 実装レビュー中
PC: Reo-Desktop

## 進捗

- 利用者待ち: なし
- [x] 1. やり方を決める(完了条件: 設計の節に、直す11のファイルと足す3つのフック、消す・直す・移す行が文のまま書いてある。ADR 3件を書いた)
- [/] 2. やり方を見直す(依存: 1)(完了条件: レビューの節の設計への指摘4件を、どれも設計の節と ADR で直し、ADR 0071-1・0071-2・0071-3 が採用になった)
- [x] 3. チケットをコミットしたら自動で push する(依存: 2)(完了条件: `tests/test_push_after_ticket_commit.py` の13件が通り、skill `task-team-messaging` の SKILL.md に「push」が0件。13件が通り、「push」は0件)
- [x] 4. 役割の skill と一緒に task-team-messaging が読まれる(依存: 2)(完了条件: `tests/test_add_messaging_skill_to_team_roles.py` の4件が通り、skill `task-team-se`・`task-team-pg`・`task-team-qa` の SKILL.md に「`task-team-messaging` を読んでいる」が0件。4件が通り、3つの SKILL.md とも0件)
- [x] 5. SE を起こす手順を短くする(依存: 2)(完了条件: `tests/test_remind_pin_after_starting_se.py` の3件が通り、skill `task-team-lead` の SKILL.md に「`set_pinned`」が0件で、「SE を high で起こせなければ」の行が1件。3件が通り、「`set_pinned`」は0件、その行は1件)
- [x] 6. 全体の CLAUDE.md を 200 行以内にする(依存: 2)(完了条件: `claude/CLAUDE.md` が 200 行以内で、設計の節で消す・移す4行が0件。200 行で、4行とも0件)
- [ ] 7. できたものを見直す(依存: 3・4・5・6)(完了条件: レビューの節の実装の指摘が0件)

## 難しさ

- SE: 高(ADR 0067-1 のとおり、いつも高)
- PG: 低(消す・直す・移す行は、設計の節に文のまま書いてある。フック3つも、動き・名前・つなぐ所・テストが設計の節に決まっていて、残るのは利用者に見えない中の作り。ADR 0070-2 のとおり Sonnet 5.5 の high)
- QA: 高(設計レビューで、ADR 3件が利用者の「なぜ」と README の目的と既にある ADR に合うかと、消す行が止めていた失敗が戻らないかを見る、枠を決める仕事のレビュー。Fable の3つの特徴のうち、利用者が中身を確かめられない分野の知識は要らないので、Opus)

## ゴール

規則を足し続けてきたプロンプト(全体の CLAUDE.md と skill)が肥大していないかを確かめ、食い違いを直し、要らない行を消して整理する。

範囲外: permissions・サンドボックスの設定。hooks は、プロンプトの行から移す作業のためにだけ足す。テストの大きさの印の食い違い(ファイルと git を使うテストを小と呼んでいる)は、PL に知らせ、このタスクでは直さない。

## 壁打ち

### 固まった要件

- プロンプトの食い違いを確かめ、整理する。(PL のタスクの文)
- なぜ: 規則を足し続けてきたので、プロンプトが肥大していないかが心配。(PL のタスクの文)
- 心配のもとは、費用と遅さと、増え方へのはっきりしない不安。AI が規則を守らなかったのを見たからではない。(利用者の答え)
- 範囲は、全部のプロンプト(全体の CLAUDE.md・すべての skill・`.claude/rules/` の「なぜ」)。(利用者の答え)
- 整理は今回1回で終え、行の数や意味の重なりを確かめる仕組みは足さない。(利用者の答え)
- 必ずする作業(SE のピン留め・ピン外し・effort の切り替え・コミット後の push など)は、プロンプトの行からフックに移す。hooks の変更は、利用者が頼んだ。(利用者の答え「フック化も範囲に入れて」)
- なぜ: フックに移した作業は、プロンプトに書かなくてよくなり、文量が浮く。(利用者の発言)

### 分かっていること

- プロンプトの大きさ(2026-11-12、`wc`)。
  - `claude/` の CLAUDE.md と SKILL.md を合わせた大きさは、10/22 に約 20KB、11/10 に約 76KB、今は約 100KB。
  - 全体の CLAUDE.md(`claude/CLAUDE.md`)は、10/29 に 91 行、11/10 に 189 行、今は 204 行(空の行を除くと 157 行)。
  - skill `task-team-se` の SKILL.md は、10/29 に約 4KB、今は約 20KB・266 行で、いちばん大きい。次は skill `task-team-lead` の SKILL.md の約 15KB・176 行。
  - SE のセッションは、どのターンも、全体の CLAUDE.md・skill `task-team-se`・skill `task-team-messaging` の約 43KB を読んでいる。
- 全体の CLAUDE.md の「なぜ」(`.claude/rules/global-claude-md.md` 101行目)に「全体は 200 行以内」とあり、今の 204 行はこれを越えている。
- Anthropic の Claude Code の best practices(https://code.claude.com/docs/en/best-practices 。2026-11-12 に読んだ)には、次のことが書いてある。
  - CLAUDE.md は 200 行未満に保つのがすすめ。
  - CLAUDE.md の行が守られないのは、ファイルが長くなって行が埋もれたか、例外の無い決まりで hook にすべきもののどちらか。
  - たいていの指針には例外があり、目の前のコードを見ている Claude の方が、前もって書いた規則よりうまく決められることが多い。
- 機械で確かめられる食い違いは、今は無い。
  - プロンプト・仕様・用語集が指す ADR の番号は、どれも `docs/adr/` にある。
  - 置き換え済みの ADR 11件を指している行は無い。
  - 採用の ADR は、どれもどこかの行から指されている。
  - ファイルをまたいで同じ文の行は4種類だけ(「原則がぶつかったときは、番号の小さい方を先にする。」など)。
- 決まりの行の字数(60字まで)と、足した行の要らない語は、hook `check_rule_length.py`・`ask_about_written_lines.py` が既に確かめている。行の数と、行どうしの意味の重なりを確かめる仕組みは無い。
- 同じ会話で前のターンと同じ先頭の文は、キャッシュから読まれ、Opus 5.5 と Sonnet 5.5 では入力の値段の 0.05 倍になる。キャッシュに書くときは、1時間の保持で 2 倍(https://platform.claude.com/docs/en/build-with-claude/prompt-caching 。2026-11-12 に読んだ)。
- 決まりの行の多くは ADR で決めたもので、採用した ADR で書き換えられるのは状態の行だけ。ADR で決めた行を消すには、その ADR を廃止か置き換え済みにする新しい ADR が要る。

### 効くか逆効果か

- 効く。全体の CLAUDE.md は、自分の決まり(200 行以内)と Anthropic のすすめを越えた。行が埋もれて守られなくなると、README の目的(agent-config を読めばすぐ AI 駆動開発に最適な環境ができる)に逆らう。
- 費用への効き目は小さい見込み。CLAUDE.md と skill は会話の先頭にあり、2ターン目からはキャッシュの 0.05 倍で読まれる。効くのは、セッションを起こすたびのキャッシュへの書き込みの分。
- 食い違いは、番号や同じ文のような機械で見つかる形では無い。整理の中身は、行どうしの意味の重なりと、Claude が自分で決められる行を消すこと。
- 逆効果になりうるのは2つ。
  - 行の多くは、前に起きた失敗を止めるために足したもの。消すと、その失敗が戻りうる。
  - 全部を一度に直すと、ADR の廃止と置き換えが一度に増え、利用者が中身を確かめきれない(README の「なぜ」の認知負荷)。

### 決まっていない問い

- なし(利用者が設計に進めると言った)

## 受け入れ条件

1. チケットの md を足す・直す・消したコミットの後に、フックが、コミットした作業ツリーのブランチを push する。
2. 上流の無いブランチでは、フックが、リモートと HEAD を指して push する。
3. チケットに触れないコミットと、リモートの無いリポジトリと、ブランチに居ない HEAD では、フックが push しない。
4. push に失敗したら、フックが git の出力を Claude に知らせる。
5. SE・PG・QA の skill を読んだ直後に、フックが skill `task-team-messaging` の本文を Claude に渡す。
6. `name` が `-se` で終わるセッションを起こした直後に、フックが、そのセッションをピン留めするよう Claude に知らせる。
7. skill `task-team-messaging` の SKILL.md に、push の行と、見出し「チケットの今は、ほかの PC からも見える」が無い。
8. skill `task-team-se`・`task-team-pg`・`task-team-qa` の SKILL.md に「始めるとき、skill `task-team-messaging` を読んでいる。」が無い。
9. skill `task-team-lead` の SKILL.md の、SE を起こす手順に、`set_pinned` の行が無く、「effort は、SE が high、PG と QA が medium で起こす。(ADR 0059-1・0071-2)」と「SE を high で起こせなければ、`set_session_effort` で high に替えてから依頼を送る。(ADR 0071-2)」がある。
10. skill `task-team-lead` の SKILL.md の名前の行は「`title` は `<タスク名> SE`、`name` は `<タスクの番号>-se` の形。PG と QA も同じ。」。
11. skill `task-team-lead` の SKILL.md に、閉じる前のピン外しの行と、`wrap_up` のあとの本文の行が無く、チケットのコミットの行に「push」が無い。
12. 全体の CLAUDE.md は 200 行以内で、force push の行・公開の入口の行・モジュールの単位の行・install の行が無い。
13. skill `module-layout` の SKILL.md にモジュールの単位の2行があり、リポジトリ直下の CLAUDE.md に install の行がある。

## 設計

### 読んだ ADR

- 書き換える行に付いた番号: 0012-2・0022-2・0047-3・0056-5・0057-2・0059-1・0067-1。
- 0067-1 の捨てた案5の根拠(PL が medium)は、ADR 0070-1 で PL が Opus 5.5 の high になり、無くなった。PL が high でないときは、今のやり方を残す(ADR 0071-2)。
- 0057-2 の理由4(閉じる前にピン留めを外す手順が要る)は、ADR 0071-3 で一部を置き換える。

### 探したもの(ADR 0068-1)

- 探した語: フック・push・ピン留め・`set_pinned`・effort・`task-team-messaging`・`additionalContext`。`claude/hooks/`・`docs/specs/`・`claude/skills/`・CLAUDE.md を grep した。
- push をするフックは無い。`block_history_erasing_push.py` は、履歴を消す push を止めるだけ。
- skill を読んだ後と、セッションを起こした後に掛かるフックは無い。
- 道具の結果の後に Claude に知らせるフックは、プロンプトを保存した後にだけ掛かる(`check_rule_length.py` など)。

### 消す行の決め方

1. フック・deny・アプリが必ずする作業か、必ず止める作業を書いた行は消す。
2. 同じときに読む別の文書と同じ規則の行は、1か所にだけ残す。
3. 1つのリポジトリでだけ要る行は、そのリポジトリの CLAUDE.md へ移す。
4. 道具の今の作りや、今の ADR と食い違う行は直す。

- 全部のプロンプトを読んで、当たったのが下の行。
- 当たらなかったもの: skill `draw-figure`・`explain-to-non-experts`・`notion-learning-log`・`notion-todo`・`prompt-structure`・`restructure-modules`・`team-kanban`・`team-kanban-page`・`ui-mockup` と、`.claude/rules/` の3つ。

### 直すファイル(どれも PG)

1. `claude/CLAUDE.md`(200 行以内にする)
   - 消す: 「- force push は `--force-with-lease` でしている。」(素の `--force` は deny、`--force-with-lease` は ask で、設定が守っている。決め方1)
   - 消す: 「- ほかのモジュールは、公開の入口だけを使っている。(ADR 0012-2)」(skill `module-layout` の、見出しに ADR 0012-2 の付いた「ほかのモジュールが使うものは、公開の入口から出している。」と同じ規則。決め方2)
   - skill `module-layout` へ移す: 「- モジュールは、利用者が画面のナビやメニューで選ぶ行き先ごとにある。画面の無いシステムでは、扱うデータのまとまりごとにある。」(モジュールを作るときに読む skill の中身。決め方2)
   - リポジトリ直下の CLAUDE.md へ移す: 「- agent-config の main にマージしたものは、`install.ps1 -Yes` か `install.sh --yes` で入れている。」(決め方3)
2. `CLAUDE.md`(リポジトリ直下)
   - 末尾に足す: 「- main にマージしたものは、`install.ps1 -Yes` か `install.sh --yes` で入れている。」
3. `claude/skills/module-layout/SKILL.md`
   - 「### 目指す状態: 業務の画面・処理・データの出し入れが、その業務のモジュールにある」の下の、いちばん上に足す: 「- モジュールは、利用者が画面のナビやメニューで選ぶ行き先ごとにある。」「- 画面の無いシステムでは、扱うデータのまとまりごとにある。」(1行にすると 60 字を越える)
4. `claude/skills/task-team-lead/SKILL.md`
   - 消す: 見出し「### 目指す状態: サイドバーの上には、利用者が話す PL と SE が出ている(ADR 0057-2)」と、その下の「- SE は、起こしたら、`set_pinned` でピン留めしている。」(フック `remind_pin_after_starting_se.py` が知らせる。決め方1)
   - 直す: 「- 名前は `<タスク名>-se`・`<タスク名>-pg`・`<タスク名>-qa`。」→「- `title` は `<タスク名> SE`、`name` は `<タスクの番号>-se` の形。PG と QA も同じ。」(`start_session` の `name` は `[a-z0-9-]` の 24 字までで、タスク名の多くは入らない。このタスクの PG と QA の name は「0071-prompt-consisten-3」「0071-prompt-consisten-2」に切られた。決め方4)
   - 直す: 「- 起こすときの effort は、3つとも medium。(ADR 0059-1)」→「- effort は、SE が high、PG と QA が medium で起こす。(ADR 0059-1・0071-2)」
   - 直す: 「- SE を起こしたら、`set_session_effort` で high に替えてから、依頼を `SendMessage` で送る。(ADR 0067-1)」→「- SE を high で起こせなければ、`set_session_effort` で high に替えてから依頼を送る。(ADR 0071-2)」(PL が high でないと、`start_session` で high を選べない)
   - 直す: 「- まだ始めていないチケットは、`small-chestnut` のリポジトリなら既定のブランチにコミットし、push している。」→「- まだ始めていないチケットは、`small-chestnut` のリポジトリなら既定のブランチにコミットしている。」(push はフック。決め方1)
   - 直す: 「- 終えるときは、作業ブランチでチケットとそのフォルダを消し、コミットして push している。(ADR 0022-2)」→「- 終えるときは、作業ブランチでチケットとそのフォルダを消し、コミットしている。(ADR 0022-2)」(同じ)
   - 消す: 「- 子セッションを閉じるときは、先に SE のピン留めを `set_pinned` で外している。(ADR 0057-2)」(`archive_session` は、ピン留めしたセッションを閉じずに、そう返す。ADR 0071-3。決め方1)
   - 消す: 「- 報告は `wrap_up` のあとの本文で出している。」(アプリの指示が、`wrap_up` のあとの本文に報告を書かせている。決め方1)
5. `claude/skills/task-team-lead/CLAUDE.md`
   - 直す: 「- 起こすときの effort は、PL の effort を越えられない。SE は、起こしてから high に替える。」→「- 起こすときの effort は、PL の effort を越えられない。PL が high なら、SE は high で起こせる。」
6. `claude/skills/task-team-messaging/SKILL.md`
   - 消す: 見出し「### 目指す状態: チケットの今は、ほかの PC からも見える(ADR 0056-5)」と、その下の「- チケットをコミットしたら、作業ブランチを push している。」「- リモートの無いリポジトリでは、push を飛ばしている。」(フック `push_after_ticket_commit.py` がする。決め方1)
7. `claude/skills/task-team-se/SKILL.md`・`claude/skills/task-team-pg/SKILL.md`・`claude/skills/task-team-qa/SKILL.md`
   - 消す: 「- 始めるとき、skill `task-team-messaging` を読んでいる。」(フック `add_messaging_skill_to_team_roles.py` が渡す。決め方1)
8. `.claude/rules/hooks.md`
   - 末尾に足す:
     - 「### 目指す状態: 道具を使った直後に例外なくする作業を、Claude が覚えていなくても抜かさない(ADR 0071-1)」
     - 「- チケットの push は `push_after_ticket_commit.py`、`task-team-messaging` を読むのは `add_messaging_skill_to_team_roles.py` がしている。」
     - 「- アプリの道具をフックから呼べるかは分からないので、SE のピン留めは `remind_pin_after_starting_se.py` が知らせている。」
     - 「- 利用者は、必ずする作業をフックに移して、プロンプトの文量を浮かせたい。」
9. `claude/user-settings.json` の `hooks`
   - `PostToolUse` の matcher `Bash|PowerShell` の組の末尾に、`push_after_ticket_commit.py` を足す。
   - `PostToolUse` に、matcher `Skill` の組を足し、`add_messaging_skill_to_team_roles.py` をつなぐ。
   - `PostToolUse` に、matcher `mcp__ccd_session__start_session` の組を足し、`remind_pin_after_starting_se.py` をつなぐ。
   - command は、今ある行と同じ形 `P=python3; python3 -c '' 2>/dev/null || P=python; "$P" "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/<ファイル>"`。
   - install は `claude/hooks/` のファイルをみな配るので、install のスクリプトは直さない。

### 足すフック(どれも PG。ADR 0071-1 の番号は、各ファイルの先頭の説明の文に付ける)

- 3つとも、Claude Code の PostToolUse の JSON を stdin で受け、Claude に知らせる文は stdout に `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "<文>"}}` で出し、exit 0 で終わる。知らせることが無ければ何も出さない。
- 外部(git・ファイル)に触る所は、関数の引数で渡し、テストで差し替える。

1. `claude/hooks/push_after_ticket_commit.py`(ADR 0071-1・0056-5)
   - `tool_name` が Bash か PowerShell で、`tool_input.command` に `git commit` を含むときだけ動く。
   - HEAD を見て push する作業ツリーは、`git -C <パス> commit` なら <パス>。無ければ、`git commit` より前の最後の `cd <パス>` か `Set-Location <パス>` の <パス>。どちらも無ければ入力の `cwd`。相対パスは入力の `cwd` から読み、パスを囲む引用符は外す。
   - チケットは、HEAD のコミットで足した・直した・消した `.md` のうち、HEAD かその親での中身の冒頭5行に「ステータス: 」で始まる行があるもの。
   - チケットが無い・リモートが無い・HEAD がブランチに居ないときは、何もしない。
   - リモートは `origin`。無ければ `git remote` の1行目。
   - 上流があれば `git push`、無ければ `git push -u <リモート> HEAD`。
   - push したら「チケットのコミットを <リモート>/<ブランチ> へ push した。」を、失敗したら「チケットのコミットの push に失敗した:」と git の出力を知らせる。
2. `claude/hooks/add_messaging_skill_to_team_roles.py`(ADR 0071-1)
   - `tool_name` が Skill で、`tool_input.skill` が `task-team-se`・`task-team-pg`・`task-team-qa` のどれかのときだけ動く。
   - `${CLAUDE_CONFIG_DIR:-~/.claude}/skills/task-team-messaging/SKILL.md` の、先頭の `---` で囲んだ所を除いた本文を、「skill `task-team-messaging` も読む。」の次の行から続けて知らせる。
   - そのファイルが無ければ、何もしない。
3. `claude/hooks/remind_pin_after_starting_se.py`(ADR 0071-1・0057-2)
   - `tool_name` が `mcp__ccd_session__start_session` で、`tool_input.name` が `-se` で終わるときだけ、「起こした SE を、`set_pinned` でピン留めする。(ADR 0057-2)」を知らせる。

### 作る仕様

- `docs/specs/push_after_ticket_commit.py.md`・`docs/specs/add_messaging_skill_to_team_roles.py.md`・`docs/specs/remind_pin_after_starting_se.py.md`。
- 冒頭は `# <ファイル名>`、節は `## ADR` と `## 動き`。
- ADR の節は、上の「足すフック」の各ファイルの括弧の番号と題。動きの節は、各ファイルの行を、外から見える動きの文で書く。

### テスト一覧

| テスト名 | 大きさ | 受け入れ条件 |
|---|---|---|
| `tests/test_push_after_ticket_commit.py` の test_チケットを足したコミットの後に作業ブランチをpushする(コマンドは `git commit -m y` で、入力の `cwd` の HEAD を見る) | 小 | 1 |
| test_git_Cで指した作業ツリーのHEADを見てpushする(`git -C x commit -m y`) | 小 | 1 |
| test_cdで移った作業ツリーのHEADを見てpushする(`cd "x" && git commit -m y`) | 小 | 1 |
| test_チケットを消したコミットの後にもpushする | 小 | 1 |
| test_ステータスの行が冒頭5行目にあるmdはチケットと見る | 小 | 1 |
| test_ステータスの行が6行目にあるmdはチケットと見ない | 小 | 3 |
| test_上流の無いブランチではリモートとHEADを指してpushする | 小 | 2 |
| test_originが無ければgit_remoteの1行目のリモートへpushする | 小 | 2 |
| test_チケットに触れないコミットの後にはpushしない | 小 | 3 |
| test_リモートの無いリポジトリではpushしない | 小 | 3 |
| test_ブランチに居ないHEADではpushしない | 小 | 3 |
| test_git_commitでないコマンドの後には何もしない | 小 | 3 |
| test_pushに失敗したらgitの出力をClaudeに知らせる | 小 | 4 |
| `tests/test_add_messaging_skill_to_team_roles.py` の test_SEとPGとQAのskillを読んだ後にtask_team_messagingの本文を渡す | 小 | 5 |
| test_ほかのskillを読んだ後には何も渡さない(`task-team-lead` と `draw-figure`) | 小 | 5 |
| test_task_team_messagingのSKILL_mdが無ければ何も渡さない | 小 | 5 |
| test_渡す本文から先頭のfrontmatterを除く | 小 | 5 |
| `tests/test_remind_pin_after_starting_se.py` の test_nameがseで終わるセッションを起こした後にピン留めを知らせる(`0071-se`) | 小 | 6 |
| test_nameがseで終わらないセッションの後には知らせない(`0071-pg` と `0071-sea`) | 小 | 6 |
| test_nameの無いstart_sessionの後には知らせない | 小 | 6 |

- 受け入れ条件 7〜13 はプロンプトだけの変更なので、テストを作らず、次で確かめる。
  - `python -m unittest discover -s tests` が通る(SKILL.md の決まりの行が 60 字以内)。
  - `wc -l claude/CLAUDE.md` が 200 以下。
  - 受け入れ条件 7〜13 の文を、それぞれのファイルで grep して、無い文は0件、ある文は1件。
  - `claude/user-settings.json` を `python -c "import json; json.load(open(...))"` で読め、3つのフックのファイル名がそれぞれ1回ずつ出る。

## 実装

- コミット: (このコミット)。ブランチ `claude/0071-prompt-consistency-cleanup-79841d`。
- 足したフック3つ: `claude/hooks/push_after_ticket_commit.py`・`add_messaging_skill_to_team_roles.py`・`remind_pin_after_starting_se.py`。`claude/user-settings.json` の `PostToolUse` につないだ(3つとも各1回)。
- 足した仕様3つ: `docs/specs/` の同名の `.py.md`。足したテスト: 13件・4件・3件(テスト一覧のとおり、どれも小)。
- 消す・直す・移す行は、設計の節の文のとおりに直した(`claude/CLAUDE.md`・リポジトリ直下の `CLAUDE.md`・`module-layout`・`task-team-lead` の SKILL.md と CLAUDE.md・`task-team-messaging`・`task-team-se`・`task-team-pg`・`task-team-qa`・`.claude/rules/hooks.md`)。
- 設計との違い1つ: `claude/skills/task-team-lead/CLAUDE.md` の直しは、1行が 65 字で上限 60 字を越えたので、「- 起こすときの effort は、PL の effort を越えられない。」と「- PL が high なら、SE は high で起こせる。」の2行にした。
- 流したもの: `python -m unittest discover -s tests` が 111 件通った(lint のコマンドは無い)。
- 受け入れ条件 7〜13 は grep で確かめた: `task-team-messaging` の「push」0件、3つの役割の「を読んでいる」0件、`task-team-lead` の `set_pinned` 0件・「SE を high で起こせなければ」1件、`claude/CLAUDE.md` 200 行で消す・移す4行0件、`module-layout` の移した行1件、リポジトリ直下の install の行1件。
- 実際の git での通し(一時リポジトリに push)は、実行が許可されず、していない。git は偽物に差し替えたテストだけで確かめた。

## レビュー

### 設計レビュー(QA、35ced4f)

- 設計1: `push_after_ticket_commit.py` は入力の `cwd` で git を動かすが、`git -C <作業ツリー> commit` や `cd <作業ツリー> && git commit` で別の作業ツリーにコミットしたときの場所が決まっていない。skill `task-team-lead` の SKILL.md 111〜113行目のとおり PL が既定のブランチの作業ツリーで未着手のチケットをコミットすると、フックは cwd の HEAD を見て push せず、109行目から push の行も消えるので、受け入れ条件1が果たせない。
- 設計2: テスト名の「コマンドは `cd x && git commit -m y`」で、git を x と入力の `cwd` のどちらで動かすかが二通りに読める。設計1と合わせて、どこの HEAD を見るかを設計の節に書く。
- 設計3: ADR 0071-2 と、skill `task-team-lead` の CLAUDE.md の直し「PL は high なので、SE は high で起こせる。」は、PL が high でないときを決めていない。SKILL.md 75行目は PL が `claude-opus-5-5` の high でない場合を想定していて、そのとき `start_session` の effort は PL 以下しか選べず(道具の説明)、`set_session_effort` の行も消えるので、SE が high にならない(ADR 0067-1 に反する)。
- 設計4: 「子セッションを閉じるときは、先に SE のピン留めを `set_pinned` で外している。(ADR 0057-2)」を消すのに、それを決めた ADR 0057-2(決めたこと「ピン留めを外してから閉じる」・理由4)を置き換える ADR が無い。チケットの「分かっていること」の最後の行のとおり、ADR 0071-1 に入れるか、0057-2 の一部を置き換える ADR が要る。
- テスト一覧・ADR の番号・仕様の作り方には、指摘なし。Fable の印(ADR を消す・同じ決まりを3回変える)は無い。

### 設計への指摘の直し(SE)

- 設計1・2: 「足すフック」の1に、HEAD を見る作業ツリーの決め方を書き、テスト一覧に `git -C` と `cd` の2件を足した。
- 設計3: ADR 0071-2 に、PL が high でないときは起こしてから high に替えることを足した。skill `task-team-lead` の SKILL.md の `set_session_effort` の行は、消さずに、その場合だけの行に直す。CLAUDE.md の直しは「PL が high なら」にした。
- 設計4: ADR 0057-2 の、閉じる前にピン留めを外す手順を、ADR 0071-3 で置き換えた。0057-2 は採用のまま。

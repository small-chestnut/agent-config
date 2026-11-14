ステータス: 実装レビュー済み
PC: Reo-Desktop

## 進捗

- 利用者待ち: なし
- [x] 1. やり方を決める(完了条件: 設計の節に、共通の skill の全文と、直すファイル11個が並んでいる)
- [x] 2. やり方を見直す(依存: 1)(完了条件: レビューの節に設計レビューの結果が3件ある)
- [x] 3. 共通の skill を作り、知らせ方の規則を移す(依存: 2)(完了条件: `claude/skills/task-team/SKILL.md` の表が13行で、`claude/skills/task-team-messaging/` は0件)
- [x] 4. 役割の skill から、表と同じ受け持ちを言う行を消す(依存: 3)(完了条件: 消えた行が4行)
- [x] 5. 役割の skill を読むと、フックが共通の skill を渡す(依存: 3)(完了条件: テスト一覧のテスト4件が通る。確かめた結果: 4件が通った)
- [x] 6. できたものを見直す(依存: 4・5)(完了条件: レビューの節に実装レビューの結果が1件ある)
- [ ] 7. インストール先から古い skill とフックを消す(依存: 6)(完了条件: 設計の「マージの後」の古いファイルが0件)

## 難しさ

- SE: 高(いつも高。ADR 0067-1)
- PG: 低(フックの名前と変え方・テスト・設定のパスを、設計と SE が直した仕様がみな決めている)
- QA: 高(設計レビューで、役割の受け持ちという規則そのものが目的に合うかを見る)

## ゴール

task-team の PL・SE・PG・QA が受け持つ作業が、どの役割も読む共通の skill の表で切り分けられ、PL が設計の中身を決めて SE に渡すことが無い。

なぜ: LogiFee の R-0784 のチームで、SE が手段の決めを PL に求め、PL が自分の判断で答えて、SE の方針を変えさせた。利用者は、設計判断を負うのは SE で PL の役割はチームの管理だと考え、役割の受け持ちを、チーム全体として何かを書いた共通の skill と、役割でだけ要る規則を持つ役割の skill に切り分けたい。

範囲外: PL が見つけたタスクで PL が書くタスクの文の中身と、ほかのタスクが main に入って進行中のタスクの前提が変わった場面の扱い。インストールのスクリプトが、リポジトリから消した skill とフックをインストール先からも消すこと。

## 壁打ち

### 固まったこと

- 話の場面: チームがもう動いているタスクについて、利用者が PL に、疑問や要望を後から話した。
- タスクの設計判断を負うのは SE。PL の役割はチームの管理。
- きっかけ: LogiFee の R-0784 のチーム(2026-11-13〜14)。SE が「PL に決めてほしい」と手段の問い(要確認ファイルの列の形、案件の依頼者を決めるときに自社宛ての請求書を数えるか、など)を送り、PL が自分の判断で答えて、SE はそれに従って方針を変えた。そのうち1つは誤りだった。PL は上海の関連会社を「自社」と読み、決まり(最初の請求書の請求先)に無い除外を足した。
- 原因: どの役割の skill も、自分の受け持ちだけを書き、ほかの役割の受け持ちを書いていない。PL の側には SE から決めを求められたときの行が無く、SE の側には手段を PL に回さない行が無い。全体の CLAUDE.md の「手段は自分で決める・足りない目的と『なぜ』は利用者に聞く」は、task-team の中で PL を利用者の代わりと読める。
- 利用者の案: skill を2段に分ける。共通の skill には、チーム全体として何か(開発チームであること・セッションがどの役割に分かれるか)と、作業ごとに各役割がしてよいか(◯✕)の表を書く。役割ごとの skill は、「開発チームの PL(SE・PG・QA)である」ことと、その役割でだけ要る規則だけを持つ。
- 利用者は、この形で設計に進めると言った。
- 利用者は、共通の skill に新しく置く目的と目指す状態の文(`claude/skills/task-team/SKILL.md` の「# 原則1」の1つ目の目的と目指す状態)に合意し、フックを変えることを認めた。

## 受け入れ条件

1. skill `task-team-lead`・`task-team-se`・`task-team-pg`・`task-team-qa` を読んだ直後に、skill `task-team` の SKILL.md の、先頭の `---` で囲んだ所を除いた本文を、「skill `task-team` も読む。」の次の行から続けて Claude に知らせる。
2. ほかの skill とツールの後には、何もしない。
3. skill `task-team` の SKILL.md が無ければ、何もしない。
4. skill `task-team` に、チームの成り立ちの行と、作業ごとに受け持つ役割の表と、受け持たない作業を頼まれたら返す行がある。
5. 表で「目的・「なぜ」・業務の事実を利用者に聞く」と「要件と設計を決める」に◯が付くのは、SE だけ。
6. skill `task-team-messaging` の規則の行は、みな skill `task-team` にあり、skill `task-team-messaging` は無い。
7. 役割の skill から、表と同じ受け持ちを言う4行が消えている。
8. 役割の skill の description が、task-team のどの役割の手順かを言っている。
9. ADR とチケットのほかに、`task-team-messaging` と `add_messaging_skill_to_team_roles` を指す所が無い。
10. インストール先に、古い skill とフックのファイルが無い。
11. どの SKILL.md の箇条書きの行も、60字以内。

## 設計

ADR: 0083-1(採用)。設計で読んだ ADR は、0024-1・0056-1・0056-2・0064-2・0071-1。

### 作る・直すファイル(11個)

| ファイル | すること | する人 |
|---|---|---|
| `claude/skills/task-team/SKILL.md` | 作る(下の「共通の skill と役割の skill」) | SE(済み) |
| `claude/skills/task-team-messaging/SKILL.md` | `git rm` で消す(本文は共通の skill に移る) | SE(済み) |
| `claude/skills/task-team-lead/SKILL.md` | 下の「共通の skill と役割の skill」のとおり直す | SE(済み) |
| `claude/skills/task-team-se/SKILL.md` | 同上 | SE(済み) |
| `claude/skills/task-team-pg/SKILL.md` | 同上 | SE(済み) |
| `claude/skills/task-team-qa/SKILL.md` | 同上 | SE(済み) |
| `claude/hooks/add_messaging_skill_to_team_roles.py` | `git mv` で `claude/hooks/add_team_skill_to_team_roles.py` にし、下の「フックの直し」のとおり直す | PG |
| `claude/user-settings.json` | `PostToolUse` の `Skill` のフックのパスを、`add_team_skill_to_team_roles.py` にする | PG |
| `.claude/rules/hooks.md` | 「`task-team-messaging` を読むのは `add_messaging_skill_to_team_roles.py`」を、「`task-team` を読むのは `add_team_skill_to_team_roles.py`」にする | SE(済み) |
| `docs/specs/add_messaging_skill_to_team_roles.py.md` | `git mv` で `docs/specs/add_team_skill_to_team_roles.py.md` にし、仕様を書き直す | SE(済み) |
| `tests/medium_test_add_messaging_skill_to_team_roles.py` | `git mv` で `tests/medium_test_add_team_skill_to_team_roles.py` にし、テスト一覧のテストにする | PG |

SE(済み)の行は、仕様(SKILL.md とフックの仕様)と文書なので、SE が設計のコミットで直した。PG が直すのは、残りの3つ。

ADR はどれも、状態の行のほかは書き換えない。古い ADR に残る `task-team-messaging` の名前は、そのときの決定の記録なので直さない。

### 共通の skill と役割の skill

`claude/skills/task-team/SKILL.md` は、SE が設計のコミットで作った。「# 原則1」の1つ目の目的と、その下の目指す状態・表・規則が新しく足した所で、ほかは、`task-team-messaging` の SKILL.md の6〜46行目をそのまま移した所。

役割の skill は、SE が設計のコミットで次のとおり直した。

| ファイル | 直し |
|---|---|
| `task-team-lead` | 「タスクの中身には答えていない。PL が答えるのは、進み具合だけ。」を消した |
| `task-team-lead` | 「子セッションから戻った本番環境の作業と、CLAUDE.md の安全の原則に関わる指摘は、利用者に判断を聞いている。」を消した |
| `task-team-lead` | 「skill `task-team-messaging` の届け方」を「skill `task-team` の届け方」にした |
| `task-team-se` | 「SE が書くのは、文書だけ。」を消した |
| `task-team-qa` | 「QA が書き換えるのは、チケットと ADR の状態の行だけ。」を消した |
| 4つとも | description の「〜する PL(SE・PG・QA)のときの手順」を「〜する、task-team の PL(SE・PG・QA)のときの手順」にした |

消した4行は、どれも共通の skill の表の行と同じ受け持ちを言う。同じ規則は1か所にだけ置く(skill `prompt-structure`)。役割の skill に残すのは、受け持つ作業をどうするかの手順。

### フックの直し

`claude/hooks/add_team_skill_to_team_roles.py` は、今のフックから次の所だけを変える。

- docstring の1行目: `PL・SE・PG・QA の skill を読んだ直後に、skill task-team の本文を Claude に渡す(Claude Code の PostToolUse フック。ADR 0071-1・0083-1)。`
- docstring の残り: `task-team-se・task-team-pg・task-team-qa` を `task-team-lead・task-team-se・task-team-pg・task-team-qa` に、`task-team-messaging` を `task-team` にする。
- `ROLE_SKILLS = ("task-team-lead", "task-team-se", "task-team-pg", "task-team-qa")`
- 定数 `MESSAGING = "task-team-messaging"` を `TEAM = "task-team"` にし、使う所も替える。
- 関数 `messaging_message` を `team_message` にし、呼ぶ所も替える。

### フックの仕様

`docs/specs/add_team_skill_to_team_roles.py.md`(SE が設計のコミットで直した)。

### マージの後(する人: PL)

インストール(`install.ps1 -Yes`)は、リポジトリから消したファイルをインストール先から消さない。インストールの後に、次の古いファイルを、対象と理由を利用者に伝えてから `trash` でゴミ箱に移す。`~/.claude-work` があれば、その下の同じファイルも移す。

- `~/.claude/skills/task-team-messaging/`(残すと、古い知らせ方の skill が skill の一覧に出て呼ばれうる)
- `~/.claude/hooks/add_messaging_skill_to_team_roles.py`(どこからも呼ばれないファイル)

### テスト一覧

| テスト名 | テストサイズ | 受け入れ条件 |
|---|---|---|
| `test_PLとSEとPGとQAのskillを読んだ後にtask_teamの本文を渡す` | 中 | 1 |
| `test_ほかのskillを読んだ後には何も渡さない`(`task-team` と `draw-figure` を subTest で) | 中 | 2 |
| `test_task_teamのSKILL_mdが無ければ何も渡さない` | 中 | 3 |
| `test_渡す本文から先頭のfrontmatterを除く` | 中 | 1 |

一時フォルダに SKILL.md を置いて読むので、どれも中(今のテストと同じ)。

文書だけの受け入れ条件の確かめ方:

| 受け入れ条件 | 確かめ方 |
|---|---|
| 4・5 | `claude/skills/task-team/SKILL.md` を開き、表が13行で、2つの行の◯が SE の列だけかを見る |
| 6 | `claude/skills/task-team-messaging/` が無く、今の `task-team-messaging` の10〜46行目と、`task-team` の「## 目的: 利用者が、かんばんと…」から最後までが、`diff` で同じ |
| 7・8 | `git diff main -- claude/skills/task-team-lead/SKILL.md claude/skills/task-team-se/SKILL.md claude/skills/task-team-pg/SKILL.md claude/skills/task-team-qa/SKILL.md` の消えた行が9行(設計の4行・description の古い4行・`task-team-lead` の「`task-team-messaging` の届け方」の古い1行)で、足した行が5行(description の4行と「`task-team` の届け方」の1行)だけ |
| 9 | `git grep -n -e task-team-messaging -e add_messaging_skill_to_team_roles -- . ':!docs/adr' ':!docs/tasks'` が0件 |
| 10 | 「マージの後」の古いファイルが、`~/.claude` と `~/.claude-work` の下に0件 |
| 11 | 既にあるテスト `tests/medium_test_skill_md_bullet_length.py` が通る |

## 実装

- フックを `git mv` で `claude/hooks/add_team_skill_to_team_roles.py` にし、設計の「フックの直し」のとおり直した(`ROLE_SKILLS` に `task-team-lead` を足し、`MESSAGING`→`TEAM`、`messaging_message`→`team_message`)。
- `claude/user-settings.json` の `PostToolUse` の `Skill` のフックのパスを `add_team_skill_to_team_roles.py` にした。
- テストを `git mv` で `tests/medium_test_add_team_skill_to_team_roles.py` にし、テスト一覧の4件にした。
- 実行した結果:
  - `python -m unittest tests/medium_test_add_team_skill_to_team_roles.py`: 4件が通った。
  - `python -m unittest discover -s tests -p "*test_*.py"`(小と中の全部): 113件が通った(`medium_test_skill_md_bullet_length.py` を含む)。
  - `git grep -n -e task-team-messaging -e add_messaging_skill_to_team_roles -- . ':!docs/adr' ':!docs/tasks'`: 0件。
- lint のコマンドは、このリポジトリの CLAUDE.md に無い。

## レビュー

### 設計レビュー

- 仕様(`docs/specs/add_team_skill_to_team_roles.py.md` と、仕様にあたる SKILL.md)は、設計のコミットで SE が直す決まり(skill `task-team-se`「動きを変えるときは、設計のコミットで仕様を直している」)だが、設計では PG が直すことになっている。
  - 直した所: SKILL.md 6つ・フックの仕様・`.claude/rules/hooks.md` を、SE が設計のコミットで直した。設計の表の「する人」を SE(済み)にした。
- ADR 0083-1 の「対象」に7つのモジュールを並べているが、CLAUDE.md は、いくつものモジュールに及ぶ ADR の対象を「全体」とする。
  - 直した所: 「対象: 全体」にし、状態を「採用」にした。
- 受け入れ条件7・8の確かめ方「`git diff main` で消えた行が設計の4行だけ」は、description 4行と task-team-lead 82行目の直しも消えた行に出るので、そのとおりには確かめられない。
  - 直した所: 確かめ方を、消えた行9行と足した行5行の内訳で言う形にした。

### 実装レビュー

- `claude/skills/task-team/SKILL.md` の「task-team は、1つのタスクを PL・SE・PG・QA のセッションで進める開発チーム。」は、利用者が合意した設計の文(コミット 015b4e8 の「共通の skill の全文」)の「4つの」が消えている。設計への問いを通した直しではなく、60字の上限にも当たっていない。

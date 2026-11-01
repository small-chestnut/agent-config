ステータス: 実装レビュー中

# ゴール

PL が自分でマージするタスクの記録は、作業ブランチを push する前に消え、`docs/tasks` には進行中のタスクの記録だけがある。記録を消しても、PL が振るタスクの番号は、前に使った番号と重ならない。

範囲外: 記録だけのリポジトリと `small-chestnut` が所有しないリポジトリの記録を消すこと、SE・PG・QA の skill と `docs/adr`・`docs/specs` を変えること、PL の報告に消した記録を取り出すコマンドを載せること。

# 受け入れ条件

1. skill `task-team-lead` に「番号は、main の履歴にある記録の名前と、進行中のチームの名前の中で、最大の番号の次。」の行があり、「番号は、main の記録と、…」の行が無い。
2. skill `task-team-lead` に「main の履歴にある記録の名前は、`git log main --format= --name-only -- <記録を置くフォルダ>` で引いている。」の行がある。
3. skill `task-team-lead` に「push の前に、作業ブランチで記録と記録のフォルダを消し、コミットしている。(ADR 0022-2)」の行が、「QA が通したか、PG が直したと知らせたら、作業ブランチを push している。」の行の次にあり、「マージの直前に、…」の行が無い。
4. skill `task-team-lead` に「`small-chestnut` が所有しないリポジトリと、記録だけのリポジトリでは、記録を消さない。(ADR 0022-2)」の行が、3 の行の次にある。
5. skill `task-team-lead` に「PG に頼む前に、記録を消したコミットを `git revert` で戻している。(ADR 0022-2)」の行が、「CI が赤なら、そのチームの PG に直しを頼んでいる。」の行の次にある。
6. skill `task-team-lead` の報告の行が「CI が緑になってから、子セッション3つを `archive_session` で閉じ、ブランチとテスト結果を利用者に報告している。」で、報告に記録のパスが無い。
7. skill `task-team-lead` の見出し「終わったタスクは、リポジトリに残り、チームは閉じている」が「終わったタスクは、変更がリポジトリに残り、記録は消え、チームは閉じている」になっている。
8. skill `task-team-lead` の、1〜7 のほかの行は、変える前と同じである。
9. `docs/tasks` に、タスク 0001〜0021 の記録と `0003-user-as-worker-briefing/` が無く、この記録だけがある。
10. `docs/adr/0022-2-delete-records-before-push.md` が skill `task-team-se` の ADR の形で「置き換える: 0022-1」の行を持ち、`docs/adr/0022-1-delete-finished-records.md` の状態が「置き換え済み(0022-2)」である。
11. `python -m unittest discover -s tests` が全部通る。

# 設計

書き換える `claude/skills/task-team-lead/SKILL.md` の行のうち、ADR の番号が付いているものは無い。見出し(原則1「受け渡しの記録が、タスクごとに1つのファイルにある」と「終わったタスクは、リポジトリに残り、チームは閉じている」)にも無い。この SKILL.md がモジュール `task-team-lead` の仕様なので、仕様はこの SKILL.md を直す。新しい名前は無い(「記録のフォルダ」は skill `task-team-pg` と `task-team-se` が既に使う語)。

利用者が SE の問いに答えて決めたこと: 記録だけのリポジトリでは、終わった記録を残す。記録は、マージの前に消す。PL の報告に、消した記録を取り出すコマンドは載せない。

ADR: `docs/adr/0022-2-delete-records-before-push.md`(状態: 採用)。実装レビューの指摘(消すコミットが CI を通らずにマージされる)を受けて、`docs/adr/0022-1-delete-finished-records.md` を置き換えた。

## 手順

1. PG: `claude/skills/task-team-lead/SKILL.md` を、次の表のとおりに直す。表の行番号は main の SKILL.md のもの。表に無い行は変えない。

   | 場所 | 変える前 | 変えた後 |
   |---|---|---|
   | 33行目 | `- 番号は、main の記録と、進行中のチームの名前の中で、最大の番号の次。` | `- 番号は、main の履歴にある記録の名前と、進行中のチームの名前の中で、最大の番号の次。` |
   | 33行目の次に足す | — | ``- main の履歴にある記録の名前は、`git log main --format= --name-only -- <記録を置くフォルダ>` で引いている。`` |
   | 80行目 | `### 目指す状態: 終わったタスクは、リポジトリに残り、チームは閉じている` | `### 目指す状態: 終わったタスクは、変更がリポジトリに残り、記録は消え、チームは閉じている` |
   | 82行目(`- QA が通したか、…push している。`)の次に足す | — | `- push の前に、作業ブランチで記録と記録のフォルダを消し、コミットしている。(ADR 0022-2)` |
   | その次に足す | — | ``- `small-chestnut` が所有しないリポジトリと、記録だけのリポジトリでは、記録を消さない。(ADR 0022-2)`` |
   | 87行目(`- CI が赤なら、そのチームの PG に直しを頼んでいる。`)の次に足す | — | ``- PG に頼む前に、記録を消したコミットを `git revert` で戻している。(ADR 0022-2)`` |
   | 88行目 | ``- CI が緑になってから、子セッション3つを `archive_session` で閉じ、ブランチ・テスト結果・記録のパスを利用者に報告している。`` | ``- CI が緑になってから、子セッション3つを `archive_session` で閉じ、ブランチとテスト結果を利用者に報告している。`` |

2. PG: `docs/tasks` の、タスク 0001〜0021 の記録21ファイルと `docs/tasks/0003-user-as-worker-briefing/` を `git rm -r` で消す。この記録(`0022-delete-finished-records.md`)は消さない。どれも git にコミット済みで、履歴から取り出せる(CLAUDE.md 原則1「git にコミット済みのものは、完全に消している」)。消す前に、対象(この手順の文)と理由(ADR 0022-2)を利用者に伝える。
3. PG: `python -m unittest discover -s tests` を流し、結果を「実装」の節に書く。

この記録は、手順1 で足す行のとおり、PL が push の前に作業ブランチで消す。

## テスト一覧

文書だけの変更なので、テストは作らない。

| 確かめ方 | 受け入れ条件 |
|---|---|
| `git diff main -- claude/skills/task-team-lead/SKILL.md` が、手順1 の表の7か所だけ | 1〜8 |
| `git ls-files docs/tasks` が `docs/tasks/0022-delete-finished-records.md` の1行だけ | 9 |
| ADR 0022-2 を skill `task-team-se` の「ADR は、決まった形で1つのフォルダにある」「置き換えた古い ADR へ、新しい ADR からたどれる」の行と見比べ、ADR 0022-1 の状態の行を見る | 10 |
| `python -m unittest discover -s tests` の結果(足した行の字数は `tests/test_skill_md_bullet_length.py` が見る) | 11 |

# 実装

- `claude/skills/task-team-lead/SKILL.md` を、設計の表のとおりに7か所直した(`git diff main` は追加の行と変えた行が表の7か所だけ)。レビューの指摘を受けた設計の直し(ADR 0022-2)に合わせて、消す行を push の前に移し、CI が赤のときに `git revert` で戻す行を足した。
- `docs/tasks` の 0001〜0021 の記録21ファイルと `0003-user-as-worker-briefing/` を `git rm -r` で消した(対象と理由は設計の手順2と ADR 0022-2)。`git ls-files docs/tasks` はこの記録の1行だけ。
- ADR 0022-1・0022-2 は SE の作成済みで、変えていない。
- テストは作らない(設計のテスト一覧)。`python -m unittest discover -s tests`: 64 件、OK。lint のコマンドはこのリポジトリの CLAUDE.md に無い。
- 設計の変更は無い。

# レビュー

- 設計: 手順1 で足す「push の前に、作業ブランチで記録と記録のフォルダを消し、コミットしている。」のあと、CI が赤なら PG に直しを頼む行(SKILL.md 87行目)が残るが、そのとき PG が読み書きする記録が作業ブランチに無い。
- 設計: 見出し「終わったタスクは、リポジトリに残り、チームは閉じている」(SKILL.md 80行目)を変えないが、その下に記録を消す行が入り、見出しと行が食い違う。受け入れ条件6 がこの見出しの直しを妨げる。
- 実装: SKILL.md 89行目「マージの直前に、作業ブランチで記録と記録のフォルダを消し、コミットしている。」の消すコミットは CI が緑になった後に足されるので、83行目「作業ブランチの CI が全部緑になってから、…マージする。(ADR 0009-3)」を通らずにマージされる。

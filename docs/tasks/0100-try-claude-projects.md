# 0100-try-claude-projects

ステータス: 実装中
PC: Reo-Desktop

## 進捗

- 利用者待ち: 設計の「許可を受ける操作」1〜6の許可 [0100-try-claude-projects PG](#local_07c2a662-7d4a-496b-80a8-6960daf87a31)
- [x] 1. 何を試して確かめるかを決める(完了条件: 利用者が、試す範囲を見て、設計に進めると言う)
- [/] 2. 自分のアカウントでプロジェクトの画面を開けるかが分かる(依存: 1)(完了条件: 利用者のブラウザで、プロジェクトを作る画面が出るか、出ないと分かる)
- [ ] 3. 試したプロジェクトの Overview で、自分を待っているスレッドを見る(依存: 2)(完了条件: R2-1)
- [ ] 4. 決まりが届いたかの表を見る(依存: 3)(完了条件: R1-1・R2-2)
- [ ] 5. 統合を続けるかを決める(依存: 4)(完了条件: 利用者が表を見て、続けるかやめるかを答える)
- [ ] 6. 試したプロジェクトと環境が片付いている(依存: 5)(完了条件: R1-2)

## 難しさ

- SE: 高(公式文書に書かれていない所を、利用者のアカウントを使って、小さく安全に確かめるやり方を自分で決める)
- PG: 高(公式文書に画面の操作が細かく書かれておらず、利用者のアカウントの画面で、どの操作が設計の操作かを自分で見分ける)
- QA: 低(結果の表を、設計の判定の表と受け入れ条件に照らす)

## ゴール

Claude の「プロジェクト」機能のクラウドのスレッドに、クラウドの環境のセットアップスクリプトで agent-config をインストールすれば、agent-config の決まりが届くかを、小さく試して確かめる。

範囲外: task-team をプロジェクト機能に置き換えること。QA の独立を保てるかと、この PC が要る仕事をローカルのスレッドにできるかを確かめること。

## 要件

### R1 クラウドのスレッドに決まりが届くかを試す

- 要件: まず「決まりを届ける」だけを小さく試す(利用者が「タスクにする」と答えた)。全体の CLAUDE.md・skill・フック・deny の4つを、スレッド1本で試す(利用者が、表を見て「設計に進める」と答えた)。
- なぜ: 利用者が統合で一番得たいのは、task-team に書いてある手順と規則を、Anthropic の「プロジェクト」機能にカバーさせて減らすこと。
- 受け入れ条件 R1-1: `result.md` に、4つのそれぞれが「届いた」「届かない」「確かめられない」のどれかで書かれ、根拠のスレッドの出力が、そのまま付いている
- 受け入れ条件 R1-2: 試すために作ったプロジェクトと環境が、アーカイブされている

### R2 肩代わりの働きを、同じスレッドで見る

- 要件: 同じスレッドで、利用者を待つことが Overview の「Waiting on you」に出るかと、コーディネーターがスレッドを開始して報告を受けるかを見る(利用者が「設計に進める」と答えた)。
- なぜ: R1 と同じ。減る見込みの規則([covered-rules.md](0100-try-claude-projects/covered-rules.md))は、この2つの働きが肩代わりする見込みのもの。
- 受け入れ条件 R2-1: 利用者が自分の画面で Overview を見て、スレッドが「Waiting on you」に出たか出なかったかを答え、`result.md` に書かれている
- 受け入れ条件 R2-2: コーディネーターが開始したスレッドの数と、スレッドの終わりがプロジェクトの会話に出たかが、`result.md` に書かれている

### 分けたタスク

### 決まっていない問い

## 設計

### ADR

今は書かない。サブタスク5で利用者が決めたことを、SE が ADR にする(手順 8)。

読んだ ADR: 0087-4(install.sh が置くもの)。書き換える行は無い。

### 置くファイルと名前・データ

- [setup-script.sh](0100-try-claude-projects/setup-script.sh): 環境に貼るセットアップスクリプト。この PC の一時フォルダで実行し、`fetch=git`・`install exit=0` と出て、CLAUDE.md・settings.json・skills・hooks・rules が置かれた。(R1)
- [thread-message.md](0100-try-claude-projects/thread-message.md): プロジェクトの会話に送る文。(R1・R2)
- `0100-try-claude-projects/result.md`: PG が書く結果。1つ目に判定の表、2つ目に R2 の結果、3つ目にスレッドの出力をそのまま。(R1-1・R2-1・R2-2)
- 環境とプロジェクトの名前は、どちらも `agent-config-trial`。プロジェクトに、リポジトリ・指示・ファイルは付けない。モデル・effort・ネットワークは、初めから選ばれているもの。(R1)
- agent-config は公開リポジトリで、チケットのコミットは push される。`result.md` に、利用者の名前・メールアドレス・アカウントの URL・トークンを書かない。画面のスクリーンショットはリポジトリに置かず、共有ノートのフォルダの `0100-trial/` に置いて、ファイル名だけを「実装」の節に書く。(R1-1)

公式文書で確かめた事実(2026-11-25 に web-fetch のサブエージェントが読んだ):

| 決まり | セットアップスクリプトで `~/.claude/` に置いたとき |
|---|---|
| `CLAUDE.md` | 読まれる(https://code.claude.com/docs/en/cloud-environments の Add personal preferences without committing to the repo) |
| `skills/` | 書かれていない。claude.ai のアカウントで有効にした skill は、プロジェクトのスレッドに読まれる(https://code.claude.com/docs/en/skills の Where skills live) |
| `settings.json` のフックと deny | 書かれていない。利用者の PC の `~/.claude/settings.json` は読まれない(https://code.claude.com/docs/en/settings の Settings in cloud sessions)。リポジトリの `.claude/settings.json` のフックと permissions は、プロジェクトのスレッドでは効かない(https://code.claude.com/docs/en/claude-projects の What threads pick up from your repositories) |

- セットアップスクリプトは、Claude Code の起動の前に、Ubuntu 24.04 で root として実行される。終わった後のファイルは保存され、後のセッションに使い回される(https://code.claude.com/docs/en/cloud-environments の Setup scripts・Environment caching)。
- 環境は、画面からは削除できず、アーカイブだけができる(https://code.claude.com/docs/en/cloud-environments )。プロジェクトはアーカイブでき、Unarchive で戻せる(https://code.claude.com/docs/en/claude-projects )。
- プロジェクトで使う環境は、Project settings > Environment で選ぶ。リポジトリの無いプロジェクトも作れる(https://code.claude.com/docs/en/claude-projects )。
- 最初のプロジェクトでは、Claude が自分で1ターン動き、スレッドを1本始めることがある(https://code.claude.com/docs/en/claude-projects の Your first batch)。
- スレッドの許可の問いは、そのスレッドの中でだけ答えられる(https://code.claude.com/docs/en/claude-projects の Unblock a thread waiting on approval)。
- 肩代わりの見積もり: task-team の規則 258 行のうち 72 行(28%)。一覧は covered-rules.md。
- プロジェクト機能の文書に書かれていないもの: スレッドどうしのやりとり・独立したレビュー・マージの担当(https://code.claude.com/docs/en/claude-projects )。このため、SE・PG・QA のやりとりの規則は、消えずに書き換えになる。
- クラウドのスレッドは使い捨ての VM で動くので、PC のファイルには触れない(https://code.claude.com/docs/en/cloud-environments )。フックと deny が届かないときに守りが弱くなるのは、GitHub のリポジトリへの操作。

### 手順

外部の操作をする前に、PG は下の「許可を受ける操作」を PL に知らせ、利用者の許可が届いてから始める。操作は Claude in Chrome でする。画面が手順と違うときと、手順に無い操作が要るときは、操作せずに「設計への問い」にする。

許可を受ける操作(スレッドが使った利用枠は戻らない。環境のアーカイブを戻す手順は、公式文書に無い。プロジェクトのアーカイブは戻せる):

1. 利用者の Chrome で claude.ai/code を開いて見る
2. クラウドの環境 `agent-config-trial` を作る
3. プロジェクト `agent-config-trial` を作り、環境を選ぶ
4. プロジェクトの会話に thread-message.md の文を1回送る(スレッド1本)
5. プロジェクトを作った直後に Claude が自分でスレッドを始めたら、止める
6. 終わった後、プロジェクトと環境をアーカイブする

手順:

1. 利用者の Chrome で claude.ai/code を開き、プロジェクトを作る画面が出るかを見る。出なければ、`result.md` に書き、手順 7 に進む。(R1)
2. 環境 `agent-config-trial` を作り、Setup script に setup-script.sh の中身を貼って保存する。保存した中身がファイルと同じことを、画面で確かめる。(R1)
3. プロジェクト `agent-config-trial` を作り、Project settings > Environment で環境 `agent-config-trial` を選ぶ。プロジェクトを作った直後に Claude が自分でスレッドを始めたら、それを止めて、`result.md` に書く。(R1・R2)
4. プロジェクトの会話に、thread-message.md の文を送る。スレッドが許可を求めて止まったら、PG は答えず、止めた文を `result.md` に書いて、「利用者がする操作」の操作 B を頼む。(R1・R2)
5. スレッドが番号 8 の問いを出したら、Overview のスクリーンショットを撮り、操作 A を頼む。(R2-1)
6. 利用者が答えた後、プロジェクトの会話にスレッドの終わりが出たかを見る。スレッドの出力を `result.md` にそのまま写し、次の表で判定する。(R1-1・R2-2)

| 決まり | 「届いた」 | 「届かない」 |
|---|---|---|
| 全体の CLAUDE.md | 番号 1 に「命題: AI 駆動開発の最適化。」がある | 番号 1 に無く、番号 3 に `install exit=0` がある |
| skill | 番号 5 の「Base directory for this skill」が、番号 4 の HOME の `.claude/skills/` の下 | 番号 2 に `task-team-pg` が無いか、番号 5 で呼べず、番号 3 に `install exit=0` がある |
| フック | 番号 7 の2つ目の push に「リモートの履歴を消す push なので止めました」がある | 番号 7 の2つ目の push が止められずに終わり、番号 4 の hooks の一覧が空でない |
| deny | 番号 6 の `rm -r` が、permissions の規則による拒否として止められ、`ls` に `/tmp/trial/deny` が出る | 番号 6 の `rm -r` が止められずに終わり、番号 4 の deny の数が 0 でない |

   - どちらにも当たらないものは「確かめられない」とし、理由を1行書く。`rm -r` か push を止めたのが Auto mode や Claude の判断のとき、番号 3 に `fetch=failed` があるとき、番号 4 の HOME と番号 3 の HOME が違うときも「確かめられない」。
   - 番号 5 の「skill `task-team` も読む。」で始まる文が届いたかは、フックの行の根拠に添える。番号 7 と食い違えば、両方を書く。
   - 確かめ方: 判定の表の4行の根拠の文が、3つ目のスレッドの出力の中にそのままあることを、ファイルを検索して確かめる。

7. コミットし、SE に「実装」の節を読むよう `SendMessage` で知らせてターンを終える。(R1・R2)
8. SE が結果の表を利用者に見せ、統合を続けるかやめるかを聞き、答えを ADR に書く。続けるなら、次にすることを「分けたタスク」に書く。QA に設計レビューを頼む。(R1・R2)
9. QA から実装を頼まれたら、PG がプロジェクトと環境をアーカイブし、アーカイブの一覧に `agent-config-trial` が2つとも出ることを見て、「実装」の節に書き、QA に実装レビューを頼む。(R1-2)

### 利用者がする操作

操作 A と B には、元に戻せないものは無い。サブタスク 6 のアーカイブは PG がする。

操作 A(手順 5 で必ず):

- 何を: 自分の画面でプロジェクト `agent-config-trial` の Overview を開き、スレッドが「Waiting on you」に出ているかを見てから、スレッドを開いて「はい」と答える。
- ゴールにどうつながるか: かんばんと「利用者待ち」の規則を、Overview が肩代わりできるかが分かる。
- なぜ利用者の手でか: 肩代わりされるのは利用者への見え方なので、利用者が見て決めるため。
- 手順: PG が出すプロジェクトへのリンクを開く → Overview の Threads タブを見る → スレッドを開く → 「はい」と送る。
- 終わったら返すこと: 「Waiting on you に出た」か「出なかった」。

操作 B(求められたときだけ):

- 何を: Chrome でのサインイン・利用規約やベータ版の同意・スレッドの中の許可の問いに答える。
- ゴールにどうつながるか: 試験を続けられる。
- なぜ利用者の手でか: サインイン・同意・許可の承認は、AI が代わりにできないため。
- 手順: PG が出す画面のリンクを開き、答える。許可の問いは、`/tmp/trial` の中の操作か、`cat`・`ls`・`id`・`python3` での読み取りだけなら許してよい。それ以外は断る。
- 終わったら返すこと: 「済んだ」か「断った」。

### テスト一覧

| テスト名 | テストサイズ | 受け入れ条件 |
|---|---|---|

コードが変わらないので、テストは作らず、消さない。

### サブタスクの前提

## 実装

## レビュー

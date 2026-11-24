# 0100-try-claude-projects

ステータス: 壁打ち中
PC: Reo-Desktop

## 進捗

- 利用者待ち: 統合で得たいことと、試す範囲で設計に進めるかの答え([SE の会話](#local_7d0f7f68-8b47-4ccd-a27a-17b655c23f53))
- [/] 1. 何を試して確かめるかを決める(完了条件: 利用者が、試す範囲を見て、設計に進めると言う)

## 難しさ

- SE: 高(公式文書に書かれていない所を、利用者のアカウントを使って、小さく安全に確かめるやり方を自分で決める)

## ゴール

Claude の「プロジェクト」機能のクラウドのスレッドに、クラウドの環境のセットアップスクリプトで agent-config をインストールすれば、agent-config の決まりが届くかを、小さく試して確かめる。

範囲外: task-team をプロジェクト機能に置き換えること。QA の独立を保てるかと、この PC が要る仕事をローカルのスレッドにできるかを確かめること。

## 要件

### R1 クラウドのスレッドに決まりが届くかを試す

- 要件: まず「決まりを届ける」だけを小さく試す(利用者が「タスクにする」と答えた)。
- なぜ: 利用者は、プロジェクト機能がいまの仕組み(task-team)に似ていて、うまく統合できるならよいと思った。

### 分けたタスク

### 決まっていない問い

- 統合で、いちばん得たいことは何か(R1 の「なぜ」)。
- 試す範囲: 全体の CLAUDE.md・skill・フック・deny の4つを、使い捨てのプロジェクト1つとスレッド1本で確かめることでよいか。
- クラウドの環境・プロジェクトを作り、スレッドを動かす操作を、誰がするか(利用者の許可はまだ無い)。

## 設計

### ADR

### 置くファイルと名前・データ

公式文書で確かめた事実(2026-11-25 に web-fetch のサブエージェントが読んだ。決定ではない):

| 決まり | セットアップスクリプトで `~/.claude/` に置いたとき |
|---|---|
| `CLAUDE.md` | 読まれる(https://code.claude.com/docs/en/cloud-environments の Add personal preferences without committing to the repo) |
| `skills/` | 書かれていない。claude.ai のアカウントで有効にした skill は、プロジェクトのスレッドに読まれる(https://code.claude.com/docs/en/skills の Where skills live) |
| `settings.json` のフックと deny | 書かれていない。利用者の PC の `~/.claude/settings.json` は読まれない(https://code.claude.com/docs/en/settings の Settings in cloud sessions)。リポジトリの `.claude/settings.json` のフックと permissions は、プロジェクトのスレッドでは効かない(https://code.claude.com/docs/en/claude-projects の What threads pick up from your repositories) |

- セットアップスクリプトは、Claude Code の起動の前に、Ubuntu 24.04 で root として実行される。終わった後のファイルは保存され、後のセッションに使い回される(https://code.claude.com/docs/en/cloud-environments の Setup scripts・Environment caching)。
- 環境は、画面からは削除できず、アーカイブだけができる。プロジェクトの削除は元に戻せない(https://code.claude.com/docs/en/cloud-environments ・ https://code.claude.com/docs/en/claude-projects )。
- プロジェクト機能は Pro・Max・Ultra のベータ版で、スレッドは利用枠を使う(https://code.claude.com/docs/en/claude-projects )。
- `small-chestnut/agent-config` は公開リポジトリ。

### 手順

### テスト一覧

| テスト名 | テストサイズ | 受け入れ条件 |
|---|---|---|

### サブタスクの前提

## 実装

## レビュー

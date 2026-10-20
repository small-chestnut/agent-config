# agent-config

AI コーディングエージェント(Claude Code / Codex CLI)の安全設定テンプレート。
エージェントによる意図しない破壊的操作を、設定レベルで機械的にブロックする。

## 構成

```
agent-config/
├── claude/
│   ├── user-settings.json     # → 各 Claude 設定ディレクトリの settings.json(マシン保護層)
│   ├── project-settings.json  # → 各リポジトリの .claude/settings.json にコピーしてコミット
│   ├── CLAUDE.md              # → 各 Claude 設定ディレクトリの CLAUDE.md(プロンプト層・全プロジェクト共通)
│   └── skills/<名前>/SKILL.md  # → 各 Claude 設定ディレクトリの skills/<名前>/SKILL.md(手順。呼ばれたときだけ読み込まれる)
├── codex/
│   ├── safety-snippet.toml    # ~/.codex/config.toml に手動マージする安全設定(自動配置しない)
│   ├── readonly.config.toml   # → ~/.codex/readonly.config.toml(調査専用プロファイル)
│   └── AGENTS.md              # → ~/.codex/AGENTS.md(プロンプト層・全プロジェクト共通)
├── install.ps1                # Windows 用配置スクリプト
└── install.sh                 # WSL2 / Linux / macOS 用(Codespaces dotfiles でも自動実行される)
```

## 使い方

```
git clone <このリポジトリ> && cd agent-config
# Windows
powershell -ExecutionPolicy Bypass -File .\install.ps1
# WSL2 / Linux / macOS
./install.sh
```

- 既存ファイルと差分がある場合は diff を表示して確認してから上書きする
- 設定は**次のエージェントセッション起動時から**有効

## 複数アカウントを使い分ける場合

Claude Code は `settings.json`・`CLAUDE.md`・`skills/` を、環境変数 `CLAUDE_CONFIG_DIR` が指す
ディレクトリから読む(未設定なら `~/.claude`)。ログイン情報もそこに保存されるため、
別ディレクトリを指定すれば別アカウントで並行して起動できる。

**そのディレクトリには安全設定が何も入っていない。** install スクリプトで配置しないと、
rm の再帰削除も force push も素通りする。

install スクリプトは `~/.claude` に加えて `~/.claude-work` にも配置する。
ただし**そのディレクトリが既に存在するときだけ**なので、他のマシンには影響しない。
別名を使うなら install.ps1 / install.sh の `.claude-work` を書き換える。

```
# 会社アカウント側を起動する例(このウィンドウの間だけ有効)
$env:CLAUDE_CONFIG_DIR = "$HOME\.claude-work"; claude
```

セッション記録と自動メモリも `CLAUDE_CONFIG_DIR` の下(`projects/`)に移る。
既存の履歴を引き継ぎたいプロジェクトは、そのプロジェクトのディレクトリだけを
ジャンクションで共有する(`mklink /J`。管理者権限は不要)。

## 運用ルール

1. **ルールの編集はこのリポジトリ側で行う**。`~/.claude/settings.json` を直接編集しない
   (マシンごとに差分が生まれ、テンプレートの意味がなくなる)
2. ただし Claude Code は許可プロンプトで「常に許可」を選ぶと `~/.claude/settings.json` に
   allow ルールを書き込むため、自然にドリフトする。install 時の diff で気づいたら、
   残したい変更はリポジトリに取り込み、不要なら上書きする
3. **秘密情報(API キー等)は絶対にコミットしない**。`env` セクションは使わない
4. 危険なコマンドがルールをすり抜けたのに気づいたら、その場でルールを追加してコミットする
5. **ゴミ箱を空にするのは人間だけ**。エージェントの削除は trash(ゴミ箱)経由なので
   間違いに気づいたら `trash-restore` で戻せる。ディスクが逼迫したら自分で
   `trash-empty` を実行する(エージェントには deny 済みで実行させない)

## 3層の守り(このリポジトリがカバーする範囲)

| 層 | 手段 | 守るもの |
|---|---|---|
| マシン保護層 | `~/.claude/settings.json` ほか(このリポジトリ) | ローカルマシン |
| ポータブル層 | 各リポジトリにコミットする `.claude/settings.json` | clone 先のあらゆる環境 |
| サーバー側 | GitHub branch protection・トークン最小権限(**このリポジトリ外**) | リモートの共有状態 |

force push などサンドボックスを捨てても取り消せない操作は、サーバー側の層でも必ず塞ぐこと。

## Claude Code テンプレートの意図

3色の信号として設計している:
**復元できる操作は allow(青)、共有状態に触れる操作は ask(黄)、復元できない操作は deny(赤)**。

- `allow`: `trash` 系(ゴミ箱への削除)。復元可能な削除は摩擦なしで通す。
  これにより「削除して」という正当な依頼はゴミ箱経由で満たされ、エージェントが
  deny を迂回して `find -delete` 等の見慣れない手段に流れる誘因もなくなる
- `deny`: rm の再帰削除(`-r` / `-R` / `-fr` / `--recursive`、フラグ後置形も含む)/
  force push(`--force` / `-f`、フラグ後置形も含む)/ `git reset --hard` / `git clean` /
  `git checkout --` / `git stash drop・clear` / `terraform destroy` /
  ゴミ箱を完全消去する `trash-empty`・`trash-rm` /
  設定ファイル自体の編集(`Edit(~/.claude/settings.json)` 等。エージェントが自分の
  ルールブックを書き換えて deny を外す経路を塞ぐ)/
  PowerShell の `Remove-Item -Recurse` 系。deny は allow やモードより常に優先され、
  ユーザーが会話で許可しても解除されない(ルール変更はこのリポジトリ経由で行う)
- `ask`: `git push`・`git restore`・`git push --force-with-lease` は毎回確認。
  履歴書き換えを依頼するときは `--force-with-lease` を使い、プロンプトで承認して通す
  (素の `--force` は塞いだまま。安全版の with-lease で用が足りるため)
- パターンの仕様: ワイルドカード `*` は任意の位置に置ける。` *`(空白あり)は
  空白区切りを要求し、`*`(空白なし)は要求しない(`:*` は末尾 ` *` の別記法)
- 限界: 組み合わせ短フラグ(`rm -vrf` 等)や refspec 先頭の `+` による強制 push
  (`git push origin +main`)は文字列パターンでは表現できない。これらは ask
  (`git push*` は全 push を確認)が受け止める。完璧を求める場合は PreToolUse
  フックを追加する(hooks/ ディレクトリを作って同梱する)
- 私用テンプレートのため、安全ルール以外の個人設定も user-settings.json に同居させている:
  - `extraKnownMarketplaces`: 公式プラグインカタログの登録。**マーケットプレイス登録を
    消すと、そこから入れたプラグインもアンインストールされる**仕様なので、テンプレートで
    常に維持する(削除しないこと)
  - `skipWorkflowUsageWarning`: Workflow 初回警告の抑止
  - VOICEVOX ツールの allow: `tts` MCP サーバーを設定していないマシンでは
    何にもマッチしないだけで無害

## Codex CLI テンプレートの意図

Codex は Claude Code のようなコマンド単位の deny リストではなく、
**サンドボックス境界 + 承認ポリシー**で守る設計。

**最重要の注意: `~/.codex/config.toml` は Codex 本体が状態を書き込むアプリ管理ファイル**
(プラグイン・信頼済みプロジェクト・MCP サーバー・デスクトップ設定などが入る)。
テンプレートで丸ごと上書きしてはいけない。そのため install スクリプトは config.toml に
触らず、安全設定は `safety-snippet.toml` を見ながら**手動でマージ**する。

- `approval_policy`: `"untrusted"`(毎回確認)が最も安全。`"on-request"` は緩め
- `sandbox_mode = "workspace-write"` + `network_access = false`: 作業ディレクトリのみ
  書き込み可・ネットワーク遮断。なお新方式の `default_permissions` /
  `[permissions.<name>]` プロファイルもあるが、旧方式とは併用不可
- `writable_roots` にネットワーク共有を足すと被害範囲がマシン外に広がるので慎重に
- 調査だけさせたいときは `codex --profile readonly`(一切書き込ませない)
- `shell_environment_policy` でサブプロセスに渡す環境変数を最小化
  (KEY/SECRET/TOKEN を含む変数は Codex のデフォルトでも除外される)
- `danger-full-access` + `approval_policy = "never"` は使い捨てコンテナ内以外で使わない
- プロジェクト側の対応物: `AGENTS.md`(モデルへの指示。強制力はない)と
  `.codex/config.toml`(プロジェクトを trust した場合のみ読み込まれる)

## プロンプト層(CLAUDE.md / AGENTS.md)の意図

deny ルールやサンドボックスが「実行を機械的に止める層」なのに対し、CLAUDE.md /
AGENTS.md は「モデルの振る舞いを指示で誘導する層」。

- **プロンプト層は「お願い」であって「強制」ではない**。文脈次第の逸脱や
  プロンプトインジェクションで破られ得るため、enforcement をここに移さないこと。
  役割は、deny に到達する前に安全な行動(ブランチ運用・削除前の説明・with-lease)を
  選ばせること
- **短く保つ**。項目が増えるほど1項目あたりの効きが薄まる。安全規律は10行前後を維持し、
  CLAUDE.md 全体は 200 行を超えない(Claude Code 公式の目安)。書き方と、規則を足す・消す条件は
  skill `prompt-structure`(原則 → 目的 → 目指す状態 → 規則の4段)に従う
- **手順は skill に出す**。CLAUDE.md は毎セッション全文が読み込まれるが、
  `claude/skills/<名前>/SKILL.md` は本文が呼ばれたときだけ読み込まれる。特定の作業でしか
  使わない手順(既存プロジェクトの組み替え・ファイルの置き場所・画面の絵の描き方など)は skill に置き、CLAUDE.md からは1行で指す
- **CLAUDE.md の原則3「開発」は、各リポジトリを AI 駆動開発向きの形に少しずつ寄せる規則**。
  作業のついでに、動かし方・用語集・決定の記録(ADR)を足していく。
  一度に整える作業は含まない(既にあるコード・フォルダ・名前をこの形に直すのは別の変更)
- プロジェクト単位で効かせたい場合は、各リポジトリ直下に `CLAUDE.md` / `AGENTS.md` を
  コミットする(project-settings.json と同じ配布モデル)

## サンドボックス環境への自動配布

- **GitHub Codespaces**: Settings → Codespaces → dotfiles にこのリポジトリを指定すると、
  コンテナ作成時に `install.sh` が自動実行される
- **自前 Docker イメージ**: ビルド時にこのリポジトリを clone して `install.sh` を実行する

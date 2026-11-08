# agent-config

目的: 新しいシステムを開発するとき、そのリポジトリの CLAUDE.md を作りこまなくても、agent-config の設定を読めば、すぐに AI 駆動開発に最適な環境ができること。

そのために、Claude Code の設定として、次の3つを置く。

- 全プロジェクト共通の指示(`CLAUDE.md`)
- 作業ごとの手順(skill。呼ばれたときだけ読み込まれる)
- 意図しない破壊的操作を、設定で機械的に止める安全設定(deny ルール・hooks・サンドボックス)

## 構成

```
agent-config/
├── claude/
│   ├── user-settings.json     # → 各 Claude 設定ディレクトリの settings.json(マシン保護層)
│   ├── project-settings.json  # → 各リポジトリの .claude/settings.json にコピーしてコミット
│   ├── CLAUDE.md              # → 各 Claude 設定ディレクトリの CLAUDE.md(プロンプト層・全プロジェクト共通)
│   ├── skills/<名前>/SKILL.md  # → 各 Claude 設定ディレクトリの skills/<名前>/SKILL.md(手順。呼ばれたときだけ読み込まれる)
│   └── hooks/                 # → 各 Claude 設定ディレクトリの hooks/(settings.json の hooks が走らせるスクリプト)
├── tests/                     # hooks と skill のテスト(python -m unittest discover -s tests)
├── install.ps1                # Windows 用配置スクリプト
└── install.sh                 # WSL2 / Linux / macOS 用(Codespaces dotfiles でも自動実行される)
```

## インストール

```
git clone <このリポジトリ> && cd agent-config
# Windows
powershell -ExecutionPolicy Bypass -File .\install.ps1
# WSL2 / Linux / macOS
./install.sh
```

- 既存ファイルと差分がある場合は diff を表示して確認してから上書きする。`-Yes`(install.sh は `--yes`)を付けると尋ねずに上書きする
- 設定は**次のエージェントセッション起動時から**有効
- 各設定ディレクトリの `agent-config-path.txt` に、この agent-config の本体の作業ツリー(`git worktree list` の1行目)の場所を書く。ほかのリポジトリで全体の規則のずれに気づいた AI が、そこの `docs/tasks/` にチケットを足すのに使う

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
6. force push など、サンドボックスを捨てても取り消せない操作は、**サーバー側でも必ず塞ぐ**。
   GitHub の branch protection と、トークンの最小権限で、リモートの共有状態を守る(このリポジトリの外で、人がする設定)

## サンドボックス環境への自動配布

- **GitHub Codespaces**: Settings → Codespaces → dotfiles にこのリポジトリを指定すると、
  コンテナ作成時に `install.sh` が自動実行される
- **自前 Docker イメージ**: ビルド時にこのリポジトリを clone して `install.sh` を実行する

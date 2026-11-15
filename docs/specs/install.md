# install

## ADR

- 0087-4 skill のフォルダの直下のファイルは、SKILL.md のほかもみなインストールする

## 動き

- `install.ps1` は Windows で、`install.sh` は WSL2・Linux・macOS で、このリポジトリの設定を各 Claude 設定ディレクトリに置く。
- 各 Claude 設定ディレクトリは、`~/.claude` と、既にあるときだけの `~/.claude-work`。
- `claude/user-settings.json` を `settings.json` として、`claude/CLAUDE.md` を `CLAUDE.md` として置く。
- `claude/skills/<名前>/` の直下のファイルを、SKILL.md のほかもみな、`skills/<名前>/` に置く。
- `claude/hooks/` のファイルを、みな `hooks/` に置く。
- 置く先に同じ中身のファイルがあれば、そのままにする。
- 置く先のファイルの中身が違えば、`-Yes`(`install.sh` は `--yes`)のときは上書きし、対話できないときは残し、対話できるときは違いを見せて上書きするかを聞く。
- 終わりに `trash` のコマンドがあるかを確かめ、無ければ入れ方を出す。

# 0087-4 skill のフォルダの直下のファイルは、SKILL.md のほかもみなインストールする

状態: 採用
日付: 2026-11-15
対象: 全体

## 決めたこと

`install.ps1` と `install.sh` は、`claude/skills/<名前>/` の直下のファイルを、SKILL.md だけでなくみな、各 Claude 設定ディレクトリの `skills/<名前>/` に置く。

## 捨てた案

1. スクリプトを `claude/hooks/` に置く(今もみなインストールされる): hooks のフォルダは settings.json のフックが走らせるスクリプトの置き場で、フックでないスクリプトが混ざると、フォルダの名前が中身を言い表さなくなる。
2. スクリプトを agent-config のチェックアウトから直接呼ぶ: PC ごとにチェックアウトの場所が違い、Codespaces などには無いこともある。
3. スクリプトを作らず、コマンドを SKILL.md に書く: ADR 0087-1 の捨てた案4と同じ。

## 理由

1. skill の本文が使うファイルを skill のフォルダに置くのは、Claude Code の skill の作り方(https://code.claude.com/docs/en/skills の「Add supporting files」。2026-11-15 に読んだ)。skill を呼ぶと、そのフォルダの場所が「Base directory for this skill」として Claude に示される(2026-11-15 に、このタスクの SE が skill を呼んで見た)。
2. 1つのモジュール(skill)のファイルが1つのフォルダにそろう(ADR 0012-1)。

# 0020-1 skill のフォルダの外にある `claude/` のファイルの「なぜ」は、パス指定のルールに置く

状態: 採用
日付: 2026-11-01
対象: 全体

## 決めたこと

`claude/CLAUDE.md`・settings・hooks のファイルの、後で同じ機能を変えるときにも守る「なぜ」は、`.claude/rules/<名前>.md` に、冒頭の `paths` でそのファイルを指して置く。

## 捨てた案

1. `claude/hooks/CLAUDE.md` に置く: install が `claude/hooks/` の全部のファイルを各 Claude 設定ディレクトリにコピーするので、除く処理を install に足すことになる。
2. README に残す: 利用者が、README を人が読む入口にし、「意図」の節をなくすと決めた。
3. agent-config 直下の CLAUDE.md に置く: どの作業でも読み込まれる。

## 理由

1. グローバルの CLAUDE.md が「なぜ」をモジュールの CLAUDE.md に置くのは、その機能を変える AI にだけ届けるため。`claude/CLAUDE.md` はグローバルの CLAUDE.md そのもので、`claude/` に2つ目の CLAUDE.md を置けない。
2. パス指定のルールは、`paths` に当たるファイルを Claude が読むか書いたときだけ読み込まれる(https://code.claude.com/docs/en/memory#path-specific-rules)。`.claude/` は install がコピーしないので、ほかのリポジトリには入らない。

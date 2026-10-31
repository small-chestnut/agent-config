ステータス: 利用者の判断待ち(ADR 0011-1・0011-2・0011-3)

# ゴール

AI が、終わったと言う前に、自分の変更を確かめている。画面が変わる変更は、AI が動かした画面のスクリーンショットを見て確かめ、報告にその画像を付ける。テストと lint は、Claude が自分で走らせて今の中身で通るまで、Stop フックがターンを終わらせない。確かめのコマンドの頭は、各リポジトリの `.claude/verify-commands.txt` に書く。

PL が調べたずれ: Anthropic の手引き(https://code.claude.com/docs/en/best-practices)は、AI が自分の仕事を確かめる手段(テスト・build・lint・ブラウザのスクリーンショット)を持つことを一番効くとし、確かめが通るまで Stop フックでターンを終わらせないことを勧めている。agent-config には、画面を見て確かめる決まりも Stop フックも無かった。

範囲外: 画面を見たかをフックで確かめること・Codex(`codex/AGENTS.md`)の側の確かめの仕組み・サブエージェントの終わり(SubagentStop)。

# 受け入れ条件

1. Stop フックは、ターンの始めから中身が変わり、今の中身で通っていない確かめのコマンドがあれば、その頭を並べてターンを止める。
2. Stop フックは、今の中身で一覧の確かめが全部通っていれば止めない。
3. Stop フックは、ターンの始めから中身が変わっていなければ止めない。
4. 確かめのコマンドの頭で始まるコマンドが Bash か PowerShell で通ると、今の中身でその確かめが通ったと記録される。
5. パイプ・`;`・`&` を含むコマンドと、バックグラウンドで走らせたコマンドは、確かめとして数えない(`2>&1` は数える)。
6. 中身の印は、コミットしても、`docs/` の下だけを変えても変わらない。
7. 確かめのコマンドの一覧が無いリポジトリと、git の外では、フックは何もしない。
8. `claude/user-settings.json` の UserPromptSubmit・PostToolUse(Bash|PowerShell)・Stop から、フックが呼ばれる。
9. agent-config に `.claude/verify-commands.txt` があり、中身は `python -m unittest` の1行。
10. グローバルの CLAUDE.md の原則3 に、確かめのコマンドの頭を一覧に書く行と、画面が変わる変更をスクリーンショットで確かめて報告に付ける行がある。
11. `task-team-pg` に、確かめた画面の画像を記録のフォルダに置き、実装の節から指す行がある。
12. README に、Stop フックの意図と、画面の確かめの意図がある。
13. `docs/用語集.md` に、確かめのコマンド・確かめのコマンドの一覧・中身の印の行がある。
14. どの SKILL.md の箇条書きの行も 60 字以内(`python -m unittest discover -s tests` が通る)。

# 設計

決定は [ADR 0011-1](../adr/0011-1-stop-hook-checks-evidence.md)・[ADR 0011-2](../adr/0011-2-verify-commands-file.md)・[ADR 0011-3](../adr/0011-3-screenshot-check.md)(どれも提案。利用者の判断待ち)。この先は、採用されてから書く。

出典: Stop フックの入力・止め方・8回続けて止めると終わる上限は https://code.claude.com/docs/en/hooks の Stop の節。Bash と PowerShell のコマンドが 0 以外で終わると PostToolUse ではなく PostToolUseFailure になることは、同じページの PostToolUseFailure の節。

# 実装

# レビュー

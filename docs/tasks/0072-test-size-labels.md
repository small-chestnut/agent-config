# 0072-test-size-labels

ステータス: 未着手

## ゴール

`tests/` のうち、一時ファイルと git を使う4つのテスト(`test_ask_about_written_lines`・`test_check_rule_documents_changed_by_shell`・`test_check_rule_length`・`test_require_verify_before_stop`)に、中の印が付いている。リポジトリ直下の CLAUDE.md の「テストは小だけ」と、小だけ・小と中を流すコマンドが、テストの実際の大きさに合っている。

なぜ: 全体の CLAUDE.md の ADR 0009-1 では、ファイルに触るテストは中。リポジトリの CLAUDE.md はそれらを小と呼んでいて、目的に反する決まりになっている。0071 の SE が見つけた。

範囲外: テストの中身と、テストが確かめる hooks の動き。

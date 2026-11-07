# ask_removable_words.py

## ADR

- なし

## 足した行を問い返す

- プロンプトの決め方と、HEAD から足した行の取り方は、check_rule_length.py と同じ。
- プロンプトを保存すると、HEAD から足した行のうち、この保存で書いた文字列を含む行だけを、行番号付きで並べて Claude に返す。
- この保存で書いた文字列が行の一部でも、その行を問う。
- HEAD から変わっていない行は、この保存で書いた文字列を含んでいても問わない。
- 空の行とコードブロックの中の行は問わない。
- この保存で書いた文字列は、Edit では new_string、MultiEdit では各編集の new_string、Write では content。

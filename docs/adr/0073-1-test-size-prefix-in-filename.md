# 0073-1 タグの無いテストフレームワークでは、中と大のテストのファイル名の頭に `medium_`・`large_` を付ける

状態: 提案
日付: 2026-11-17
対象: 全体
置き換える: 0009-2 の、タグの無いテストフレームワークでファイル名に `.medium`・`.large` を入れる所

## 決めたこと

全体の CLAUDE.md(`claude/CLAUDE.md`)の、タグの無いテストフレームワークでのテストサイズの印を、ファイル名の中の `.medium`・`.large` から、ファイル名の頭の `medium_`・`large_` に替える。

## 捨てた案

1. 今のまま、ファイル名に `.medium`・`.large` を入れる: Python の unittest は、ファイル名が識別子でないテストを読まず、エラーも出さない。2026-11-17 に手元の Python 3.14 で、`test_x.medium.py` は `-p "*.medium.py"` でも0件だった。
2. ファイル名の終わりに `_medium`・`_large` を付ける: Go は `*_test.go` で終わるファイルだけを、Jest は既定で `.test.js`・`.spec.js` などで終わるファイルだけをテストとして拾う。終わりの形を決めるテストフレームワークで、印を付けたテストが流れない。
3. 印を `_medium` のように記号から始めるか、区切りに `-` を使う: Go は `_` か `.` で始まるファイルを無視し、`-` は Python の識別子に使えない。
4. 形を決めず、「テストフレームワークがテストとして拾う形で、ファイル名に印を入れる」とだけ書く: 拾われるかを書く人がテストフレームワークごとに調べることになり、今の規則と同じく拾われない形を選びうる。grep で探す語もリポジトリごとに割れる。
5. テストサイズごとにフォルダを分ける: ADR 0009-2 の捨てた案1 と同じく、テストを確かめる対象のモジュールのフォルダに置く決まり(skill `module-layout`)とぶつかる。

## 理由

1. `medium_`・`large_` は英字で始まり、英数字と `_` だけでできているので、頭に付けても、Python の識別子の決まりにも、Go が無視する名前の決まりにも当たらない。Jest と Node.js のテストランナーの既定の形(`.test.js` などで終わる名前)と、Go の `*_test.go` は名前の終わりで決まるので、頭の印はそれを崩さない。
2. 出典: Python unittest の Test Discovery 節「their filenames must be valid identifiers」(https://docs.python.org/3/library/unittest.html#test-discovery)、Go の Test packages 節「Files whose names begin with "_" … or "." are ignored.」(https://pkg.go.dev/cmd/go)、Jest の testMatch(https://jestjs.io/docs/configuration#testmatch-arraystring)、Node.js のテストランナー(https://nodejs.org/api/test.html#running-tests-from-the-command-line)。
3. agent-config の中では、ADR 0072-1 で同じ形(`medium_test_<対象>.py`)にし、小だけ(既定の `test*.py`)と小と中(`-p "*test_*.py"`)を選んで流せている。2026-11-17 に手元で、`medium_test_y.py` は既定の形では拾われず、`-p "*test_*.py"` で拾われた。
4. 印が名前の頭に決まった語で付くので、grep で `medium_`・`large_` を探せば見つかる(ADR 0009-2 の理由2)。

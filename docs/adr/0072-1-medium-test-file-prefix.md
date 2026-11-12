# 0072-1 agent-config の中のテストは、ファイル名の頭に `medium_` を付ける

状態: 提案
日付: 2026-11-12
対象: 全体

## 決めたこと

unittest には大きさのタグが無いので、中のテストのファイル名を `medium_test_<対象>.py` にし、小だけは discover の既定の形で、小と中は `-p "*test_*.py"` で流す。

## 捨てた案

1. 全体の既定のとおり、ファイル名に `.medium` を入れる(`test_<対象>.medium.py`)。discover は点を含む名前をモジュールとして読めず、エラーを出さずに読み飛ばすので、中のテストが一度も流れない(手元の Python 3.14 で、`-p "*.medium.py"` でも0件だった)。
2. 名前の終わりに `_medium` を付ける(`test_<対象>_medium.py`)。discover の既定の形 `test*.py` に当たり、`-p` には除く形が無いので、小だけを流すコマンドが作れない。
3. 中のテストを `tests/medium/` に分ける。ADR 0009-2 が、大きさでフォルダを分ける案を捨てている。
4. pytest に替え、マーカーで印を付ける。標準ライブラリだけで流せる今のテストに、テストを流すためだけの依存を足し、どの PC にも入れることになる。
5. 中のテストのクラスに、環境変数が無ければ飛ばす印(`unittest.skipUnless`)を付ける。環境変数を前に置く書き方が PowerShell と bash で違い、どちらも検証コマンドのプレフィックス(ADR 0011-2)で始まらなくなる。

## 理由

1. ファイル名の頭の `medium_` は grep で見つかり、discover の `-p` だけで、小だけと小と中を選んで流せる(ADR 0009-2 の理由1・2)。
2. `medium_test_<対象>.py` は Python のモジュール名として読めるので、変えた所だけを流す `python -m unittest tests/<テストのファイル>.py` がそのまま使える。
3. 大きさをファイル名の形で分けて別々に流すのは、Maven の Failsafe プラグインが結合テストを `*IT.java` などの名前の形で選ぶ(https://maven.apache.org/surefire/maven-failsafe-plugin/integration-test-mojo.html の includes の既定)のと同じ定石。

ステータス: 実装レビュー中

# ゴール

agent-config のリポジトリのルートに `.gitignore` があり、テストを走らせると自動でできる Python のキャッシュ(`__pycache__/` の下の `.pyc`)が、どのフォルダにできても git の追跡の対象にならない。タスク 0030 で `claude/hooks/__pycache__/*.pyc` を誤ってコミットしたのと同じことが、もう起きない。

範囲外: `__pycache__/` 以外の除外(エディタの設定・OS のファイルなど)、`install.ps1`・`install.sh` で配る先のリポジトリへの `.gitignore` の配布。

# 受け入れ条件

1. リポジトリのルートの `.gitignore` は、`__pycache__/` の1行だけである。
2. `python -m unittest discover -s tests` を走らせたあと、`git status --porcelain --untracked-files=all` に `__pycache__` を含む行が無い。
3. `claude/hooks/__pycache__/` と `tests/__pycache__/` の下の `.pyc` は、`git check-ignore` で無視される。
4. `git ls-files` に `__pycache__` を含むパスが無い。
5. main(65f35fe)からの差分は、`.gitignore` の追加と本記録だけである。
6. `python -m unittest discover -s tests` が全部通る。

# 設計

設定だけの変更で、コードと決まりの文書は変えない。書き換える行が無いので、集める ADR の番号は無い。用語集にも足さない(`.gitignore` は IT の用語で、このリポジトリで形や意味を決めない)。

置くファイル: リポジトリのルートの `.gitignore`。中身は次の1行。

```
__pycache__/
```

- 末尾の `/` でフォルダだけに当たり、ほかに `/` が無いので、どの深さのフォルダにも当たる(出典: git の gitignore の文書 https://git-scm.com/docs/gitignore の PATTERN FORMAT)。
- Python 3 は `.pyc` を `__pycache__/` の下にだけ作るので、`*.pyc` の行は足さない。GitHub の Python 用の雛形も `__pycache__/` を除外の先頭に置いている(https://github.com/github/gitignore/blob/main/Python.gitignore)。
- `claude/hooks/require_verify_before_stop.py` の中身の印は `git add -A` で作るので、これからはテストでできた `__pycache__/` で印が変わらなくなる。仕様の「未追跡のファイルを足すと変わる」の行は、無視したファイルを含まないので、仕様は直さない。

## 手順

| 番号 | する人 | すること |
|---|---|---|
| 1 | PG | リポジトリのルートに `.gitignore` を作り、`__pycache__/` の1行と改行だけを書く |
| 2 | PG | 確かめ: 下の「テスト一覧」の確かめ方を全部走らせる |
| 3 | PG | コミットする。本文に理由を書く: リポジトリに `.gitignore` が無く、テストでできた `claude/hooks/__pycache__/*.pyc` がタスク 0030 で誤ってコミットに入り、QA に指摘された |
| 4 | PL | main にマージし、push する。`claude/` の下は変えないので、`install.ps1 -Yes` は要らない |

## テスト一覧

設定だけの変更なので、テストは作らない。確かめ方を並べる。

| 確かめ方 | 受け入れ条件 |
|---|---|
| `cat .gitignore` が `__pycache__/` の1行だけ | 1 |
| `python -m unittest discover -s tests` を走らせ、通る | 6 |
| そのあと `git status --porcelain --untracked-files=all` に `__pycache__` を含む行が無い | 2 |
| `git check-ignore -v claude/hooks/__pycache__/x.pyc tests/__pycache__/x.pyc` が、2つとも `.gitignore:1:__pycache__/` を返す | 3 |
| `git ls-files` に `__pycache__` を含むパスが無い | 4 |
| `git diff 65f35fe --stat` が `.gitignore` と本記録だけ | 5 |

# 実装

手順 1〜3 のとおり、ルートに `.gitignore`(`__pycache__/` の1行)を作ってコミットした。確かめた結果:

- `.gitignore` の中身は `__pycache__/` と改行だけ(条件 1): OK
- `python -m unittest discover -s tests`: 64 件、OK(条件 6)
- そのあと `git status --porcelain --untracked-files=all` は `?? .gitignore`(コミット前)だけで、`__pycache__` の行なし(条件 2): OK
- `git check-ignore -v` は2つとも `.gitignore:1:__pycache__/`(条件 3): OK
- `git ls-files` に `__pycache__` のパスなし(条件 4): OK
- `git diff 65f35fe --stat`(条件 5): 下の確認のとおり `.gitignore` と本記録だけ

lint のコマンドは CLAUDE.md に無い。

# レビュー

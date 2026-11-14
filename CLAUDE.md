このリポジトリの目的と構成は README.md にある。

- 中のテストは、ファイル名の頭に `medium_` を付ける。`medium_` の付いていないテストは小。(ADR 0072-1)
- 小だけは、リポジトリのルートで `python -m unittest discover -s tests`。(ADR 0072-1)
- 小と中は、`python -m unittest discover -s tests -p "*test_*.py"`。大のテストは無い。(ADR 0072-1)
- 変えた所のテストだけは、`python -m unittest tests/<テストのファイル>.py`(いくつもなら空白で並べる)。
- ADR の「対象」に書くモジュールの名前は、skill の名前か hooks のファイル名。いくつもに及ぶなら「全体」。
- permissions・フック・サンドボックスを変えるタスクは、安全の原則のとおり利用者に頼まれてから進める。
- 全体の CLAUDE.md の安全の原則には、deny とフックに届く前に安全な行動を選ばせる文だけを置いている。
- 全体の CLAUDE.md には、利用者が頼んだ本番の作業を断らせる文を置いていない。
- main にマージしたものは、`install.ps1 -Yes` か `install.sh --yes` でインストールしている。

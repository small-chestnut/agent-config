このリポジトリの目的と構成は README.md にある。

- 中のテストは、ファイル名の頭に `medium_` を付ける。`medium_` の付いていないテストは小。(ADR 0072-1)
- 小だけは、リポジトリのルートで `python -m unittest discover -s tests`。(ADR 0072-1)
- 小と中は、`python -m unittest discover -s tests -p "*test_*.py"`。大のテストは無い。(ADR 0072-1)
- 変えた所のテストだけは、`python -m unittest tests/<テストのファイル>.py`(いくつもなら空白で並べる)。
- ADR の「対象」に書くモジュールの名前は、skill の名前か hooks のファイル名。いくつもに及ぶなら「全体」。
- README の目的とのずれは、PL が、やるかを利用者に聞かずにタスクにして進める。
- 目的に反する規則・仕様・コードも、PL が、やるかを利用者に聞かずにタスクにして進める。(ADR 0046-3)
- PL でないセッションは、それらに気づいたら、直さずに PL に知らせる。(ADR 0046-3)
- permissions・フック・サンドボックスを変えるタスクは、安全の原則のとおり利用者に頼まれてから進める。
- `claude/` 直下と hooks のファイルの「なぜ」は、`.claude/rules/` に paths 付きで置く。(ADR 0020-1)
- main にマージしたものは、`install.ps1 -Yes` か `install.sh --yes` でインストールしている。

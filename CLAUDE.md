このリポジトリの目的と構成は README.md にある。

- テストは、この階層で `python -m unittest discover -s tests`。
- ADR の「対象」に書くモジュールの名前は、skill の名前か hooks のファイル名。いくつもに及ぶなら「全体」。
- README の目的とのずれは、PL が、やるかを利用者に聞かずにタスクにして回す。
- permissions・フック・サンドボックスを変えるタスクは、原則1 のとおり利用者に頼まれてから回す。

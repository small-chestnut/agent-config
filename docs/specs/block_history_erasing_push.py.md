# block_history_erasing_push.py

## ADR

- 0105-3

## リモートの履歴を消す push を止める

- Bash・PowerShell の git push が、--force・--mirror・--prune、-d のほかの f か d を含む短いフラグ、+ で始まる refspec を含めば、当たった引数を理由に書いて止める。
- リモートのブランチを消す push(`--delete`・`-d`・`:<ブランチ>`)は、消すブランチがみな、リモートの今の先端(リモートごとに1回だけ走らせる `git ls-remote --heads <リモート>` の結果)を、手元のリモートの既定のブランチ(`refs/remotes/<リモート>/HEAD` が指すもの)が履歴に含むとき(`git merge-base --is-ancestor`)だけ通す。
- 既定のブランチそのもの・リモートに無いブランチ・先端のコミットを手元に持たないブランチ・`refs/remotes/<リモート>/HEAD` が無いリモートを消す push は止める。
- 同じ push に、ほかの消す引数(`--force`・`--mirror`・`--prune`・`+` で始まる refspec・`-d` 以外の f か d を含む短いフラグ)があれば止める。
- git は、コマンドに `-C <フォルダ>` があればそのフォルダ、無ければフックに渡る `cwd` で走らせる。消す push と同じコマンドに `cd`・`Set-Location`・`pushd`・`Push-Location` があれば、確かめるリポジトリと push するリポジトリが別になりうるので止める。
- 時間の上限は、フック全体で 20 秒にする。走らせる git ごとに、残りの時間を上限に渡す。git が失敗したか、残りの時間を使い切ったら止める。
- 消す push を止める文には、マージ済みでないなど、止めた理由とブランチの名前を書く。
- --force-with-lease を含む git push は、どの位置にあっても利用者の確認に回す。
- &&・||・;・|・改行でつないだコマンドは、1つずつ見る。止める push と確認に回す push が両方あれば止める。
- ふつうの git push と、push 以外の git のコマンドは、何も返さずに通す。

# block_history_erasing_push.py

## ADR

- なし

## リモートの履歴を消す push を止める

- Bash・PowerShell の git push が、--force・--delete・--mirror・--prune、f か d を含む短いフラグ、+ か : で始まる refspec を含めば、当たった引数を理由に書いて止める。
- --force-with-lease を含む git push は、どの位置にあっても利用者の確認に回す。
- &&・||・;・|・改行でつないだコマンドは、1つずつ見る。止める push と確認に回す push が両方あれば止める。
- ふつうの git push と、push 以外の git のコマンドは、何も返さずに通す。

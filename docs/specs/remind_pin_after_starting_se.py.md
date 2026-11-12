# remind_pin_after_starting_se.py

## ADR

- 0071-1 道具を使った直後に例外なくする作業は、プロンプトに書かずにフックに任せる
- 0057-2 サイドバーの上には、利用者が話す PL と SE が出ている

## 動き

- `start_session` で、`name` が `-se` で終わるセッションを起こした直後に、「起こした SE を、`set_pinned` でピン留めする。(ADR 0057-2)」を Claude に知らせる。
- `name` が `-se` で終わらないセッションと、`name` の無い `start_session` の後には、何も知らせない。

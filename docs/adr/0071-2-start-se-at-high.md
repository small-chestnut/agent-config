# 0071-2 SE は、`start_session` の effort に high を渡して起こす

状態: 採用
日付: 2026-11-12
対象: task-team-lead
置き換える: 0067-1 の、SE を起こしてから high に替える所

## 決めたこと

PL は SE を、`start_session` の effort に high を渡して起こす。PL が high でなく high を渡せないときだけ、起こしてから `set_session_effort` で high に替え、それから依頼を送る。

## 捨てた案

1. いつも、起こしてから `set_session_effort` で high に替える(今のやり方): ADR 0067-1 がこれを選んだ根拠は、PL が medium で、起こすときの effort が PL を越えられないことだった(0067-1 の捨てた案5)。ADR 0070-1 で PL は Opus 5.5 の high になり、根拠が無くなった。残ると、道具の呼び出しが1回と、手順の行が1行余る。

## 理由

1. `start_session` の effort は、起こすセッションの effort 以下を選べる(道具の説明)。PL は high なので、high を選べる。
2. 起こしたときから high なので、PL が high のふだんのタスクでは、依頼を送る前に替え忘れる所が無い。
3. PL が high でないときも、SE は ADR 0067-1 のとおり high で動く。skill `task-team-lead` は、PL が `claude-opus-5-5` の high でないときを利用者に伝える形で残している。

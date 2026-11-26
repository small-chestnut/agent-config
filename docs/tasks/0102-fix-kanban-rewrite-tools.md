# 0102-fix-kanban-rewrite-tools

ステータス: 未着手
PC: Reo-Desktop

## ゴール

skill `team-kanban` の書き直し方を、PL が頼むサブエージェントが今の道具で実行でき、かんばんのカードが書き直せるようにする。

起きていること(gemini の PL からの知らせ、2026-11-26、利用者の「頼んで」による): かんばんの書き直しを頼んだサブエージェントが3回とも、`datasets/cards` の `source` が指す `/_blob/…` の `cards.json` を読めず、新しいファイルをかんばんに上げる道具も無いと返した。SKILL.md の「新しいファイルをかんばんにアップロードする」「`source.url` を新しいファイルに替え、古いファイルを消す」が、今の道具(ArtifactData の読み書き・Artifact の公開ファイルの読み書き)で実行できない。

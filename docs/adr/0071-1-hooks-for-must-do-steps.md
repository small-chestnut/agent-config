# 0071-1 道具を使った直後に例外なくする作業は、プロンプトに書かずにフックに任せる

状態: 提案
日付: 2026-11-12
対象: 全体

## 決めたこと

道具を使った直後に例外なくする作業は、プロンプトの行に書かず、フックがする。フックから呼べないアプリの道具の作業は、その時点でフックが Claude に知らせる。

## 捨てた案

1. フックの `mcp_tool` で、アプリの `set_pinned` を直接呼ぶ: 文書には、呼べるのは「configured MCP server」とだけある。アプリが持つ道具の server を指せるかと、`start_session` の結果から新しいセッションの id を渡せるかは、書かれていない(https://code.claude.com/docs/en/hooks 。2026-11-12 に読んだ)。呼べなければ、エラーで止まらずに素通りする(同じ文書の non-blocking error)。試すには `~/.claude/settings.json` を書く必要があり、deny で止まる。
2. フックに移さず、2行を1行にまとめて行を減らす: SKILL.md の決まりの行は 60 字までで(テスト `test_skill_md_bullet_length`)、まとめると 60 字を越える。
3. 閉じる前のピン外しもフックにする: アプリの `archive_session` は、ピン留めしたセッションを閉じずに、そう返す(道具の説明)。フックが無くても、Claude はその返事で外す。
4. 必ずする作業を、プロンプトに書いたまま残す: 例外の無い決まりは、フック・deny・管理された設定に置くのが Anthropic の勧め(https://code.claude.com/docs/en/best-practices 。2026-11-12 に読んだ)。残すと、プロンプトの肥大のもとになる。

## 理由

1. フックがする作業は、Claude が覚えておかなくても抜けない。毎回必ずすることはフックに、が Anthropic の勧め(https://code.claude.com/docs/en/best-practices 。2026-11-12 に読んだ)。
2. フックが知らせる文(`additionalContext`)は、その道具の結果の横に置かれ、その時点でだけ Claude に届く(https://code.claude.com/docs/en/hooks 。2026-11-12 に読んだ)。毎回読むプロンプトには載らない。
3. 利用者は、必ずする作業をフックに移して、プロンプトの文量を浮かせることを選んだ。

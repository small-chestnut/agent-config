# 0047-2 ほかのリポジトリで気づいた全体の規則のずれは、install が書き残した場所の agent-config に、ずれ1件につきチケット1つを足し、agent-config の PL が聞かずにタスクにする

状態: 提案
日付: 2026-11-09
対象: 全体

## 決めたこと

agent-config の外で全体の CLAUDE.md・skill の規則のずれに気づいた AI は、install が設定ディレクトリの `agent-config-path.txt` に書き残したその PC の agent-config の `docs/tasks/` に、ずれ1件につき `drift-<英語の短い名前>.md` を1つ足し、agent-config の PL は利用者が書いたターンごとにそれを探して、聞かずにタスクにして回す(詳しい文は全体の CLAUDE.md の原則3 と、agent-config の CLAUDE.md)。

## 捨てた案

1. 返答に、agent-config の PL へ貼って送る1行を付ける: 利用者が選ばなかった。ずれを運ぶ役が利用者に残る。
2. Notion の ✅ Todo に行を作る: Notion につながっていない会話(会社のアカウントなど)からは届かない。
3. agent-config の GitHub に issue を立てる: agent-config は公開のリポジトリで、作業中のリポジトリの場面が誰でも読める。
4. 届いたずれを1つのファイルに並べる: 利用者が、ずれ1件にチケット1つを選んだ。
5. agent-config の場所を、全体の CLAUDE.md に書くか、毎回利用者に聞く: 場所は PC ごとに違い、聞くたびに利用者の手が要る。

## 理由

1. 利用者の理由: `~/.claude` の写しを直しても、次の install で上書きされて消える。ずれが agent-config に届かないと、矛盾を探して突きつける役が利用者に残る(ADR 0046-3 の理由4 で範囲外にした部分)。
2. 場所を install に書かせるのは、install はその PC の agent-config から走るので、場所を必ず知っているから。
3. チケットに作業中のリポジトリのコードとデータを写さないのは、チケットの文がタスクの文として、公開の agent-config の ADR とコミットメッセージに移るから。
4. PL が利用者の書いたターンごとに探すのは、PL がチームを起こせるのは利用者が書いたターンだけだから(skill `task-team-lead`)。task-team を通さない会話では、決定を ADR に書かずタスクにして PL に回す(ADR 0004-1)のと同じ向き。

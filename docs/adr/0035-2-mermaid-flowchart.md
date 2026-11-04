# 0035-2 進み具合の図は、mermaid の flowchart の文で書き、配置は mermaid に任せる

状態: 提案
日付: 2026-11-04
対象: draw-figure

## 決めたこと

進み具合の図は、作業と矢印と色を mermaid の `flowchart TD` の文で書き、箱と矢印の配置は mermaid に任せる。

## 捨てた案

1. SVG の座標を、描くたびに AI が計算する: 描くたびに配置が変わり、箱と矢印が重なりやすい。
2. 記録から図を作るスクリプトをリポジトリに置く: install は skill の SKILL.md だけを配るので、ほかのリポジトリの PL から使えない。

## 理由

1. mermaid は、文から図を描く広く使われている道具で、GitHub の Markdown でもそのまま図になる(https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)。
2. 作業とつながりが同じなら同じ文になり、同じ配置の図が出る。会話の中の図は、mermaid を esm.sh から読み込んで描ける(2026-11-04 に、この形の HTML を Edge で描いて確かめた)。

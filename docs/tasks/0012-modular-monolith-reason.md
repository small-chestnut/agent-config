ステータス: 利用者の判断待ち(ADR 0012-1・0012-2)

# ゴール

モジュラーモノリスを採る理由と、それが定石に沿うかが、リポジトリに残っている。理由は ADR 0012-1 に書き、今の規則の行に番号を付ける。今の決まり(グローバルの CLAUDE.md 原則3、skill `module-layout`・`restructure-modules`)を定石と照らし、ずれていた「ほかのモジュールからは公開の入口だけを使う」を ADR 0012-2 にして規則に足す。

発端: 利用者は「モジュラーモノリスも、AI駆動開発に効くんだっけ」と聞き、PL の答えのあとで「モジュラーモノリスの記述も含めて　それぞれタスク作って」と頼んだ。

利用者の理由:「AI駆動開発で大事なのは、コードのスケールと同時に、あなたが見るコンテキストまでスケールしないように、極力抑えることが命題で、そのためにモジュラーモノリスや、ADRの配置があると思っているのだけど、違う？」。

範囲外: モジュールの境目を lint やアーキテクチャのテストで止める規則と、モジュールどうしの依存を輪にしない規則。

# 受け入れ条件

1. `docs/adr/0012-1-modular-monolith.md` があり、決めたこと・捨てた案(層ごとのフォルダ・マイクロサービス・vertical slice だけ)・理由があり、理由に、利用者の理由が言葉のままと、AI の読む量が減るという理由は定石として確かめていないことが書いてある。
2. `docs/adr/0012-2-module-public-entry.md` があり、決めたこと・捨てた案・理由がある。
3. グローバルの CLAUDE.md(`claude/CLAUDE.md`)原則3 の、モジュールのフォルダに置く行に `(ADR 0012-1)` が付いている。
4. グローバルの CLAUDE.md 原則3 に、ほかのモジュールは公開の入口だけを使う行があり、`(ADR 0012-2)` が付いている。
5. `module-layout` の目的の見出しに `(ADR 0012-1)` が付き、公開の入口の目指す状態と規則があり、その見出しに `(ADR 0012-2)` が付いている。
6. `module-layout` の description に、ほかのモジュールのものを使うときが入っている。
7. README の「プロンプト層」の節に、モジュラーモノリスを採る理由(利用者の理由を言葉のまま)と、AI に効くという理由は定石として確かめていないことがあり、`(ADR 0012-1・0012-2)` が付いている。
8. `docs/用語集.md` に、モジュールと公開の入口の行がある。
9. どの SKILL.md の箇条書きの行も 60 字以内(`python -m unittest discover -s tests` が通る)。

# 設計

決定は [ADR 0012-1](../adr/0012-1-modular-monolith.md)・[ADR 0012-2](../adr/0012-2-module-public-entry.md)(どちらも提案)。手順は、利用者が採用してから書く。

## 定石との照合

| 今の決まり | 定石 | 判定 |
|---|---|---|
| 原則3・`module-layout`: 業務のまとまりごとのフォルダに、画面・処理・データの出し入れを置く | vertical slice(要求ごとに前から後ろまでまとめる)、Shopify(商取引のサブドメインごとの component) | 沿う |
| 原則3: モジュールは画面のナビの行き先ごと、画面が無ければデータのまとまりごと | Shopify・DDD はサブドメイン(業務の領域)ごと | 沿う(業務の画面のナビの行き先は業務の領域に当たる) |
| `module-layout`: どの業務のものでもないものだけを `shared/` に置く | vertical slice の、slice をまたいで共有するコードを小さくする | 沿う |
| `module-layout`: ほかのモジュールが使うものも、その業務のモジュールに置いたまま。どこから使うかの決まりは無い | Simon Brown・Spring Modulith・Shopify: モジュールは公開の API を出し、中はほかのモジュールから使わせない | ずれ → ADR 0012-2 |
| `restructure-modules`: 中身を変えずに `git mv` で動かし、前後の動きを比べる | Shopify: ファイルをまず component のフォルダへ動かし、境目はあとから整える | 沿う(直さない) |

出典:
- vertical slice: https://www.jimmybogard.com/vertical-slice-architecture/
- Shopify: https://shopify.engineering/shopify-monolith
- Spring Modulith: https://docs.spring.io/spring-modulith/reference/verification.html
- Simon Brown「Modular Monoliths」(GOTO Berlin 2018): https://files.gotocon.com/uploads/slides/conference_12/515/original/gotoberlin2018-modular-monoliths.pdf

# 実装

# レビュー

# user-settings.json

## ADR

- 0084-5 「なぜ」は、リポジトリの命題と ADR にだけ置き、「なぜ」の文書を置かない

## 動き

- 操作は戻せるかで分け、戻せる操作は allow、共有の状態を変える操作は ask、戻せない操作は deny に置く。
- `extraKnownMarketplaces` を残し、install で上書きしても、そこから入れたプラグインが消えない。

---
paths:
  - claude/user-settings.json
  - claude/project-settings.json
---

原則がぶつかったときは、番号の小さい方を先にする。

# 原則1: 安全

## 目的: 意図しない破壊的操作を、モデルの判断に頼らず止める

### 目指す状態: 操作は、戻せるかどうかで3色に分かれている

- 戻せる操作は allow、共有の状態に触る操作は ask、戻せない操作は deny。
- 正当な削除をゴミ箱で通し、deny を迂回する手段に流れる誘因を作っていない。
- 設定ファイル自体の編集を deny にし、エージェントが自分の deny を外せない。
- 履歴の書き換えは `--force-with-lease` を ask で通し、素の `--force` は塞いでいる。
- LogiFee の本番に書く `execute_plan` は ask。開発者が本番に書けないと困るので deny にしない。
- `execute_plan` を allow にしない。LogiFee の `LogiFeeMCP/README.md` が、毎回訊かせると決めている。

# 原則2: 私用

## 目的: 利用者の私用の設定が、テンプレートの更新で消えない

### 目指す状態: 安全ルールのほかの個人設定も、`user-settings.json` に残っている

- `extraKnownMarketplaces` を消していない。消すと、そこから入れたプラグインも消える。
- 安全ルールでない設定を、安全ルールでないという理由で消していない。

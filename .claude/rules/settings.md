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
- 正当な削除はゴミ箱で通し、エージェントが deny の内側で削除を終えられる。
- 設定ファイル自体の編集は deny で、deny を外せるのは利用者だけ。
- 履歴の書き換えは `--force-with-lease` を ask で通し、素の `--force` は塞いでいる。
- LogiFee の本番に書く `execute_plan` は ask。開発者は本番に書く仕事がある。
- 毎回訊くのは、LogiFee の `LogiFeeMCP/README.md` の決まり。

# 原則2: 私用

## 目的: 利用者の私用の設定が、テンプレートの更新で消えない

### 目指す状態: 安全ルールのほかの個人設定も、`user-settings.json` に残っている

- `extraKnownMarketplaces` を残している。消すと、そこから入れたプラグインも消える。

## 目的: 利用者が、返答を母語で読める

### 目指す状態: 返答の言葉が、設定で利用者の母語に決まっている

- `language` は、利用者の母語の `japanese`。

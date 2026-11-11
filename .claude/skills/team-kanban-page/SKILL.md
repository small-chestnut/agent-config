---
name: team-kanban-page
description: かんばん(Artifact「チームかんばん」)のページを直すときと、利用者のアカウントにかんばんが無くて作るときの手順。ページの元は、この skill のフォルダの index.html。
---

# 原則1: 人間側の最適化

## 目的: かんばんの見た目と動きが、どのアカウントでも同じ

### 目指す状態: ページの元は、このフォルダの `index.html` 1つ(ADR 0056-4)

- ページを直すときは、`index.html` を直してから、かんばんに書いている。
- かんばんに書くのは、`files/index.html` の `text` に、`index.html` の中身。
- 書いた後、かんばんの `data/users/me` の `check` が `passed` かを見ている。
- ページが読む項目を変えたら、skill `team-kanban` の項目の行も直している。

### 目指す状態: かんばんは、アカウントに1枚だけ

- 作る前に、Artifact の一覧に「チームかんばん」が無いことを確かめている。
- 作るときは、Artifact の型「Data」から、名前を「チームかんばん」にしている。
- `dash/meta` は、`title` が「チームかんばん」、`lang` が `ja`。
- カードのデータは、中身が `[]` の JSON のファイルを上げ、`datasets/cards` から指している。
- `datasets/cards` の `source` は、`kind` が `file`、`format` が `json`。

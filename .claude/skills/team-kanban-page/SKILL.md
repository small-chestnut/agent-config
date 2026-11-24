---
name: team-kanban-page
description: かんばん(Artifact「チームかんばん」)のページを直すときと、利用者のアカウントにかんばんが無くて作るときの手順。ページのソースは、この skill のフォルダの index.html。
---

# 原則1: 人間側の最適化 ― 利用者が、AI の出力と作業の今を、少ない負担で正確につかみ、自分の意図どおりに AI を動かせる

## 目的: かんばんのページを直しても、どのアカウントでも見た目と動きが同じ(ADR 0056-4)

- ページを直すときは、`index.html` を直してから、かんばんに書く。
- かんばんに書くのは、`files/index.html` の `text` に、`index.html` の中身。
- 書いた後、かんばんの `data/users/me` の `check` が `passed` かを見る。
- ページが読む項目を変えたら、skill `team-kanban` の項目の行も直す。

## 目的: かんばんは、アカウントに1枚だけ

- 作る前に、Artifact の一覧に「チームかんばん」が無いことを確かめる。
- 作るときは、Artifact の型「Data」から、名前を「チームかんばん」にする。
- `dash/meta` は、`title` が「チームかんばん」、`lang` が `ja`。
- カードのデータは、中身が `[]` の JSON のファイルをアップロードし、`datasets/cards` から指す。
- `datasets/cards` の `source` は、`kind` が `file`、`format` が `json`。

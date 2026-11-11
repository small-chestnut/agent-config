# 0060-reply-language

ステータス: 実装中
PC: Reo-Desktop

## 進捗

- 利用者待ち: Claude Code の再ログイン(`claude` を端末で起動して `/login`)のあと、受け入れ条件2の確認を走らせる。[0060-reply-language-pg](#local_50dfab61-717e-48bc-9df8-d2b7d74a2cc2)
- [x] 1. やり方を決める(完了条件: 設計の節がコミットされている。確かめた: 設計の節・受け入れ条件・難しさを書いてコミットした)
- [/] 2. 返答の言葉を日本語に決める設定と、その「なぜ」を足す(依存: 1)(完了条件: 足した設定で、英語の問いへの返答が日本語になる)
- [ ] 3. できたものを見直す(依存: 2)(完了条件: レビューの節の、実装への指摘が0件)

## 難しさ

- SE: 中(原因の見立てと直し方の選択はあるが、Claude Code の設定と今の規則の枠の中で決まる)
- PG: 低(足す1行と段の文が設計に書いてあり、そのとおりに書けば済む)
- QA: 低(設計レビューは無く、実装レビューは設計の文と差分が合うかを見れば済む)

## ゴール

agent-config を入れた Claude Code が、日本語でなく英語で返答することがある。その原因を突き止め、日本語で返答するようにする。

タスクの文(利用者の言葉のまま): agent-config使ってるとさ、どうも日本語じゃなくて英語の応答になってしまうことがしばしば見受けられるんだけど、なんでだろ タスクにして

範囲外: コード・コミットメッセージ・ファイル名など、返答以外に書くものの言葉は決めない。

## 壁打ち

### 調べて分かったこと

1. Claude Code の既定の返答の言葉は英語。設定の `language` に言葉の名前を書くと、Claude Code はそれを「いつもその言葉で返答する」指示として Claude に渡す(出典: https://code.claude.com/docs/en/settings-reference の `language`)。
2. agent-config が配る設定(`claude/user-settings.json`・`claude/project-settings.json`)にも、全体の CLAUDE.md・skill にも、返答の言葉を決める所が無い(2026-11-11 に grep で確かめた)。日本語で返すのは、CLAUDE.md と利用者の発言が日本語だから、という暗黙の手がかりだけ。
3. `language` は、音声入力の言葉と、自動で付くセッションの題の言葉も決める(同じ出典)。
4. 1つのセッションの文脈は、Claude Code の指示・道具の説明・道具の結果の大半が英語。PL や子セッションのターンは、英語で書かれた自動の知らせ(サブエージェントの完了・ほかのセッションの知らせなど)で始まることも多く、そのターンには日本語の利用者の発言が無い。英語に転ぶのはこういうターンだ、というのは見立てで、確かめていない。

### 固まったこと

1. 直し方は、配る設定 `claude/user-settings.json` に `"language": "japanese"` を足す形にする。音声入力の言葉とセッションの題も日本語になる。なぜ: 利用者は日本語話者で、母語でない返答は、AI の出力をつかむ負担を上げる(README の目的)。

## 受け入れ条件

1. 配る設定 `claude/user-settings.json` の `language` が `japanese` である。
2. 配る設定を読ませた Claude Code は、英語の問いにも日本語で返答する。
3. `.claude/rules/settings.md` の「原則2: 私用」の下に、目的「利用者が、返答を母語で読める」、目指す状態「返答の言葉が、設定で利用者の母語に決まっている」、規則「`language` は、利用者の母語の `japanese`。」がある。

## 設計

### 書き換える所

1. `claude/user-settings.json`: 最上位の `"theme": "auto",` の次の行に `"language": "japanese",` を足す。する人: PG。
2. `.claude/rules/settings.md`: 「原則2: 私用」の既にある目的の段の後に、次の段を足す。する人: PG。

```
## 目的: 利用者が、返答を母語で読める

### 目指す状態: 返答の言葉が、設定で利用者の母語に決まっている

- `language` は、利用者の母語の `japanese`。
```

書き換える行と見出しに付いた ADR の番号は無い。ADR は書かない(設定1行の追加で、構造・依存・インターフェースに効かない)。

### テスト一覧

設定と文書だけの変更なので、テストは作らない。確かめ方は次のとおり。する人はみな PG。

| 確かめ方 | 大きさ | 受け入れ条件 |
|---|---|---|
| `python -c "import json;print(json.load(open('claude/user-settings.json',encoding='utf-8'))['language'])"` が `japanese` を出す | — | 1 |
| リポジトリのルートで `claude -p "What is 2+2? Answer in one short sentence." --settings claude/user-settings.json` を走らせ、返答が日本語 | — | 2 |
| `.claude/rules/settings.md` を開き、3行がその段にある | — | 3 |
| `python -m unittest discover -s tests` が通る | — | (既にあるテストを壊していない) |

- 2つ目が `claude` の起動で失敗したら(ログインが要る・入れ子の起動が止められるなど)、出た文を「実装」の節に書き、サブタスク2を利用者待ちにして PL に知らせる。
- 返答が英語なら、設定の名前と値を出典(https://code.claude.com/docs/en/settings-reference の `language`)と見比べ、合っていれば「実装」の節に結果を書いて PL に知らせる(設計の前提が崩れたので、SE が見直す)。

### 入れたあとのこと

main にマージしたあとの `install.ps1 -Yes` で、`~/.claude/settings.json` に `language` が入る。効くのは次に起こすセッションから。

### サブタスクの前提

2. `--settings` は、そのファイルの設定を足して1回だけ起動する Claude Code の引数で、`~/.claude/settings.json` を書き換えない。

## 実装

- `claude/user-settings.json` に `"language": "japanese",` を `theme` の次の行へ足した。`.claude/rules/settings.md` に設計の3行の段を足した。
- 受け入れ条件1: json の `language` が `japanese` と出た。
- 受け入れ条件3: `.claude/rules/settings.md` の末尾にその段がある。
- 既にあるテスト: `python -m unittest discover -s tests` が 86 件で OK。
- 受け入れ条件2: `claude -p "What is 2+2? Answer in one short sentence." --settings claude/user-settings.json` が `Failed to authenticate: OAuth session expired and could not be refreshed` で失敗した(未確認)。再ログイン後に同じコマンドを走らせる必要がある。

## レビュー

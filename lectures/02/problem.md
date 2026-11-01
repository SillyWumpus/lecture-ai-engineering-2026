# 第2回 演習・宿題：LoRA で用語集の回答を学習し、学習前後を比較する

この回は Google Colab（T4 GPU、無料枠）で行います。Codespaces は使いません。

## この回のゴール

- 小さなモデルを LoRA で短時間学習させ、学習の前後で **何が変わり、何が変わらないか** を数字と出力で確かめる
- 用語集にある語とない語で `needs_review` を使い分け、回答内容とJSON形式を学習前後で比較する
- ファインチューニングが向く場面と向かない場面を、自分の言葉で説明できる

## 使うノートブック

- [notebooks/lora_format_tuning.ipynb](../../notebooks/lora_format_tuning.ipynb)
- Colab で開く：https://colab.research.google.com/github/matsuolab/lecture-ai-engineering-2026/blob/main/notebooks/lora_format_tuning.ipynb

講座用語集のSFTデータを題材に、`Qwen/Qwen3.5-0.8B` を LoRA で学習します。用語集にある項目は `needs_review: false` と定義を、用語集にない項目は `needs_review: true` と「用語集には記載がありません。」を返すJSON 1行が正解です。
評価は **形式遵守率**（JSONとして読め、キーが `answer` と `needs_review` のちょうど2つで、値の型が文字列と真偽値か）と、**内容正解率**（`needs_review` が正解と一致し、正解の語句が `answer` に含まれるか）に分けます。`needs_review` はモデルの一般知識ではなく、用語集への登録有無を表します。

## 事前準備（任意、5 分）

授業の前にノートブックのセクション 0〜3 を実行し、GPU の割り当て、ライブラリの導入、モデルのダウンロードができることを確かめておくと、当日の詰まりが減ります。
Colab はセッションが切れると変数が消えるので、当日はあらためて 0 から実行します。

## 演習（30分）

1. Colab でノートブックを開き、**ファイル → ドライブにコピーを保存** で自分用にコピーする
2. **ランタイム → ランタイムのタイプを変更 → T4 GPU** を選ぶ
3. `glossary.json` と `glossary_sft.jsonl` を用意してColabにアップロードし、セクション 0〜3 を上から実行する。学習前の表でJSON形式、`needs_review`、回答内容を確認する
4. セクション 4 で学習する。待ち時間に「LoRA と QLoRA の違い」の説明を読む。`trainable%` と `Training Loss` の推移を確認する
5. セクション 5〜6 で学習後を評価し、学習前と比べる
   - 比較表：`format_rate` と `content_rate` はどう変わったか
   - `退行`：学習前は通っていたのに学習後に落ちた質問（空が期待値）
   - 質問ごとの表で、JSON形式、`needs_review`、回答語句のどこで失敗したかを読む
   - 用語集にない質問は学習例に使った語と異なるので、未見の語への判定を確認する
6. セクション 7 で `result.json` を作る。要点を `lectures/02/answer.md` に書き、作業ブランチ `lec02` から自分の fork の `main` へ PR を出す（answer.md の編集は GitHub の画面上で行ってもよい）。`result.json` は `lectures/02/` に置いて PR に含めてもよい
7. **ランタイム → ランタイムを接続解除して削除**

> Colab の GPU は無料枠で使える時間に限りがあります。終わったら必ずランタイムを削除してください。
> GPU が割り当てられない、または時間内に学習が終わらないときは、ノートブックの 4b に従い、講師が T4 で実行した結果を見ながら比較と考察を進めます。提出時は `executed_training_myself` を `False` にし、自分で実行できた範囲を answer.md に書いてください。

seed を固定しても、GPU 上の学習は完全には再現しません。隣の人と「残った質問」が違っても異常ではないので、失敗の型で比べてください。

## 宿題（どれか1つで完了）

| レベル | 内容 |
|---|---|
| 基礎 | `CONFIG` の `lora_r`・`lr`・`num_train_epochs` のどれか 1 つを変えて再学習し、`format_rate`・`content_rate`・`both_rate`・最終 loss・学習時間を元の設定と並べて記録する。変えたら **ランタイム → セッションを再起動** して上から実行し、`result.json` を比べる |
| 実装 | 評価用の `TEST_CASES` に、学習データと重複しない言い換え質問や未登録語を追加し、対応する `gold` も用意する。形式・`needs_review`・回答語句のどこで正解率が変わるか考察する |
| 発展 | 用語集から作ったSFTデータで学習する方法と、第3回で作る「用語集を検索するエージェント」を比較し、用語の追加・更新や未登録語への対応でどちらが向いているか考察する |

発展のデータ作成（Codespaces で実行し、できたファイルを Colab にアップロードする）：

```bash
uv run python scripts/make_sft_dataset.py > glossary_sft.jsonl
```

各行は `messages` 形式で、assistantの回答は `{"answer": ..., "needs_review": ...}` です。用語集の全項目に対する `needs_review: false` の例に加え、評価用とは異なる未登録語への `needs_review: true` の例を8件含みます。Colab側ではJSONLの各行を `Dataset.from_list` にそのまま渡して、セクション4の `SFTTrainer` で学習します。評価用の質問は見出し語・言い換え・用語集にない語から作り、学習例と評価例の質問が重複しないようにしてください。

セクション 8（4bit で読み込んで出力を比べる）は学習をしない観察なので、どのレベルでも結果に添えてかまいません。4bit のまま学習する方法（QLoRA）は、この講座の環境（T4）では動作を確認していないため、宿題の対象外です。

## 注意

- 学習後は変数 `model` にも adapter が差し込まれています。学習前の出力を取り直すときは `tuned.disable_adapter()`（セクション 6 参照）を使うか、セッションを再起動します
- ノートブックのライブラリは動作確認した版（セクション 0 の `PINS`）に固定しています。版を変えると動かなくなることがあります

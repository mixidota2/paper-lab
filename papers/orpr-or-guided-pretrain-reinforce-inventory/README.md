# ORPR: An OR-Guided Pretrain-then-Reinforce Learning Model for Inventory Management

Must — ORラベルで事前学習し、RLOOで業務へ調整。約0.93Mの補充方策とJD菓子の現場評価。

ORで作った補充ラベルを小型モデルへ学習させ、RLで業務目標へ合わせる。約0.93MパラメータのTransformer＋VAEを用い、JDの菓子3カテゴリで保有費用−29.95%、在庫回転日数−5.27日を報告した。対象はマネジャーが選んだ高自動化SKUで、全カタログの無作為実験ではない。

本Labの焦点は、モデルを大きくする前にORの構造をラベルと報酬へ渡す設計にある。最小実験ではORラベル生成とRLOOの基準値だけを検算する。

## 読む順番

lab.yamlの問題設定と根拠を読み、[手法の説明](method.md)で式と図を対応させる。[原論文との対応](mapping.md)には最小実装の省略点を記した。著者報告とLabの検算値はresults.jsonで分離している。

## 実験を動かす

```sh
UV_CACHE_DIR=/tmp/uv-cache uv run --no-project papers/orpr-or-guided-pretrain-reinforce-inventory/run.py
UV_CACHE_DIR=/tmp/uv-cache uv run paper-lab build
```

2カテゴリ×在庫日数1〜10日の100候補を全探索する。12日の合成需要に対し、3日ごとの発注、1日のリードタイム、単価1を固定した。各候補の期末在庫累計と売り逃しを計算し、許容損失を変えて最小在庫のラベルを選ぶ。

比較対象は制約を変えた同一候補集合。TransformerやVAEの代替モデルは学習しない。別途、4つの固定報酬についてleave-one-out advantageを計算する。報酬への定数加算でadvantageが変わらないことを確かめる。

## 確認範囲を守る

**CONFIRMED — 局所検算**：在庫・販売・売り逃しの収支、100候補の制約判定、最小在庫の選択、RLOOの定数シフト不変性を確認した。

**PARTIAL — メカニズム**：シミュレーションからORラベルを選ぶ部分に限定。ニューラル方策が制約を常に守るという保証は与えていない。

**NOT TESTED**：Transformer＋VAE学習、RLOO更新、KL制約、販促の専門家適応、JDの総費用・現場効果・大規模運用。30日・菓子3カテゴリという範囲を、DeepStockのTmall全カタログ展開と同一視しない。現場の欠品費用は著者評価にも含まれない。

一次資料：[論文](https://arxiv.org/abs/2512.19001)。Pages：[Lab](https://mixidota2.github.io/paper-lab/papers/orpr-or-guided-pretrain-reinforce-inventory.html)。

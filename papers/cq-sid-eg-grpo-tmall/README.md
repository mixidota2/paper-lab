# CQ-SID：商品群を生成し、Tmallの既存ランキングにつなぐ

Efficient Generative Retrieval for E-commerce Search with Semantic Cluster IDs and Expert-Guided RL

TmallAPPのCQ-SIDは、一つのSIDから意味の近い商品群を取り出す召回チャネルだ。カテゴリ制約とquery-item対照学習で群を作り、EG-GRPOで既存の露出・クリックに合わせる。2週間のA/BでGMV +1.15%、UCTCVR +0.40%。購入の72.63%という値はチャネル構成比で、改善率ではない。

一次資料：[arXiv 2605.14434v1](https://arxiv.org/pdf/2605.14434v1)。判定：Worth Reading。

## 読み方

lab.yamlが本文と図の定義、method.mdがモデル・数式の補足、mapping.mdが一次資料との対応表。run.pyが最小実験、results.jsonが実行結果。siteは生成物である。

## 実行

```sh
uv run papers/cq-sid-eg-grpo-tmall/run.py
uv run paper-lab build
```

## 検証の境界

クラスタからの商品展開、後段の件数制限による非単調なtarget保持、同報酬群のadvantage消失、expert注入時の報酬差と一歩の勾配を確認した。群分割では上限100群のため、5,001商品なら最大51商品が残る境界も確認する。

カテゴリ表現学習、EMA codebook、Qwen2.5-0.5BのSFT、複数stepのEG-GRPO、GRPO collapseの実際の発生、CTR/CVR/GMV、40msのservingは未再現。ログのselection bias、商品展開の重複帰属、オンラインrankingの実装は不明。

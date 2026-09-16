# 原論文と実装の対応

一次資料：[PDF v1](https://arxiv.org/pdf/2605.14434v1)。公式実装へのリンクは確認した一次論文内に見つからなかった。下記はこのLab独自の説明用実装であり、公式コードではない。

| 原論文の箇所 | Labの対応 | 確認の範囲 |
|---|---|---|
| §3.1、式1–7 | method、量子化の式 | RQ-VAE/EMA/InfoNCEは説明のみ |
| Algorithm 1 | run.py split_cluster | 均等な分割件数。ランダムな商品割当は省略 |
| §3.2 | 学習段階の本文 | Qwen2.5-0.5Bを学習していない |
| 式8–10、Algorithm 2 | advantages / gradient_probe | 合成groupの初期勾配。完全なGRPOではない |
| 表1–3 | beam比較表、商品展開の操作 | toy scoreは説明用。hitrate再現ではない |
| 表4 | EvidenceのK=0/2比較 | collapseは著者解釈。toyは学習崩壊を検証しない |
| §4.5 | チャネル比率の積み上げ棒 | 50.25/58.96/72.63%は構成比。GMV/UCTCVR liftと分離 |

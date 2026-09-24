# 原論文との対応

一次資料：[arXiv:2609.04961v1](https://arxiv.org/pdf/2609.04961v1)。PDF SHA-256: `a36674fa3c4e1b4d3caf95e3c181c16292edda9a0bd9fa32900dbf00d1a9601f`。確認日：2026-09-24。

| 論文 | Lab | 実装の境界 |
|---|---|---|
| §3・図1：Boolean検索と商品側展開 | run.pyのretrieve | 合成3商品のtoken集合のみ |
| §4.1–4.2：SFTとCPV反実仮想拡張 | Core Idea、offline-index | 画像と学習は未実装 |
| §4.3：新規語、商業価値、gate付き効用 | new-terms、run.pyの固定gate | GRPOや報酬モデルは未実装 |
| 表1–2・§5.1：offline評価 | Evidence | 自動関連ラベルの限界を明記 |
| 表4・§5.3：A/B、索引、latency | online-lift | 原データ・信頼区間は未取得 |

公式コード：提供PDFでは対応リポジトリを確認できなかった。run.pyは説明用の独立実装。論文内のA/B日付と報酬ログ収集時期は前後が一致しないため、その解消は未検証。

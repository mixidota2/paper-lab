# Original Paper / Official Code Mapping

一次資料: [Balancing Trial and Reorder: A Hybrid Sequential Transformer–GBDT Ranker for On-Demand Delivery](https://arxiv.org/html/2609.16407v1)。本文・実験・限界・付録を確認（2026-09-21）。キャッシュは `/tmp/research-2026-09-21/2609.16407.html`。HTML SHA-256: `3efd76e9194c61d61c912b4d1c25fb6dfa874f66ca6c5bf6a6ccfb18220468e2`。

| 原典 | Labの対応 | 意図した省略・境界 |
| --- | --- | --- |
| §4.1–4.3 / Fig. 2 | モデルと特徴の解説 | 国間転移は主張しない |
| Eq. 6 / §4.4 | smooth_target / fit | linear pairwise代理。CatBoostは省略 |
| Appendix A | 重み比の可視化 | 公式150 retrainの再現ではない |
| Table 5 | 版別A/B表 | control・期間・対象を分離 |

公式コード: 確認した本文に、このシステムの学習・配信を再実行できる公開実装へのリンクは見つからなかった。公開の有無を網羅的に調べたという意味ではない。

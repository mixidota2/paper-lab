# Original Paper / Official Code Mapping

一次資料：[IGPO v1](https://arxiv.org/pdf/2609.04813v1)。2026-09-24にarXivから取得し、本文とPDFを確認した。PDF SHA-256: `482975f49657607611f57fd5b8c1be47ef6e30c4ce95eb940b973623a552c127`。

| 原典 | Labの対応 | 省略したもの |
| --- | --- | --- |
| Fig. 1 / §3.2 / Eqs. 3–8 | 図、method.md、portrait / search | embedding、scene profileの実更新、LLMの検索計画 |
| §3.3 / Appendix B | replay_gateと失敗例 | stochastic rollout、judge、規則の生成、統計的閾値と組合せ検証 |
| Tables 1–3 / §4.3 | FNI/FM、予算比較、未解決例の説明 | 3,000要求と在庫snapshotによる再評価 |
| Table 4 / §4.4 | A/Bの効果と分母 | 商用利用者ログ、再実験 |

公開コード：確認した一次PDFには、本手法の公式実装へのリンクを見つけられなかった。公開実装が存在しないと断定するものではない。run.pyは論文の重み・prompt・検索基盤を移植したコードではなく、観測範囲と規則の寿命を確かめる独立した人工実験である。

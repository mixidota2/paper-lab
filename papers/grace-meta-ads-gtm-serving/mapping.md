# Original Paper / Official Code Mapping

一次資料: [GRACE: Generative Recommender Acceleration Engine for Real-Time Ads Retrieval](https://arxiv.org/pdf/2608.00938v1)、arXiv v1。2026-09-22確認。PDF SHA-256: `4b0fb0a46d634f111450e471f1b5236435b68c59d03e8ccd03601bc176cadfae`。取得済みPDFは `/tmp/research-2026-09-22/2608.00938v1.pdf` を再利用した。

| 原典 | Lab | 省略 |
| --- | --- | --- |
| §4.2 | union / match | 実targeting全属性、k-way最適化 |
| §4.3 | bloom | 256-bit production hash、GPU |
| §5 | decoder解説 | 全kernel・paged KVの実装 |
| Tables 3,6 | Evidence / latency表 | 生request・GH200再測定 |

比較先STATIC/FlashTrieのLabは制約付きdecodeの計算経路を扱う。GTMのpass率をそれらのretrieval品質と直接比較しない。

公式コード: 確認したPDFに本手法の公開実装へのリンクは見つからなかった。公開の有無を網羅的に保証するものではない。

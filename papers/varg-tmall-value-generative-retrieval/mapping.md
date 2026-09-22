# Original Paper / Official Code Mapping

一次資料: [VARG: Value-Aware and Ranking-Aligned Generative Retrieval for Dynamic E-commerce Search](https://arxiv.org/pdf/2609.14493v1)、arXiv v1。2026-09-22確認。PDF SHA-256: `8ee5b5702c4432420fe3a62e890071de38add3d8dd19a359c3af609b9e4faddb`。取得済みPDFは `/tmp/research-2026-09-22/2609.14493v1.pdf` を再利用した。

| 原典 | 最小コード / 解説 | 省略 |
| --- | --- | --- |
| §3.1 Eqs. 1–5 | method / eb | RQ-VAEとQ2I学習、funnel tie-breakの実データ |
| §3.2 Eq. 6 | assign / alias_rate | 多prefix・月次rebuild |
| §3.3 Eq. 11 | ordinal | Qwen full SFT |
| §3.4 Eqs. 12–18 | reward / branch_weights | PPO optimizer、KL推定 |
| Tables 1,4,6,7 | Evidence | 著者報告、独立再現なし |

公式コード: 確認したPDFに本手法の公開実装へのリンクは見つからなかった。公開の有無を網羅的に保証するものではない。

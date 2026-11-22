# Original Paper / Official Code Mapping

一次資料: [VARG: Value-Aware and Ranking-Aligned Generative Retrieval for Dynamic E-commerce Search](https://arxiv.org/pdf/2609.14493v1)、arXiv v1。2026-09-22確認。PDF SHA-256: `8ee5b5702c4432420fe3a62e890071de38add3d8dd19a359c3af609b9e4faddb`。取得済みPDFは `/tmp/research-2026-09-22/2609.14493v1.pdf` を再利用した。

| 原典 | 最小コード / 解説 | このLabで扱わないもの |
| --- | --- | --- |
| §3.1 Eqs. 1–5 | methodの説明 / eb | RQ-VAEとQ2Iの学習、行動funnelで同順位を解消する実データ |
| §3.2 Eq. 6 | assign / alias_rate | 複数のprefix、月次の再構築 |
| §3.3 Eq. 11 | ordinal | QwenでのSFT全体 |
| §3.4 Eqs. 12–18 | reward / branch_weights | PPOの最適化、KLの推定 |
| Tables 1,4,6,7 | Evidence | 著者の値を示した。独立した再現はしていない |

公式コード: 確認したPDFの中には、この手法の公開実装へのリンクが見つからなかった。公開されていないと結論づけられるわけではない。

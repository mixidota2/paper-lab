# Original Paper / Official Code Mapping

一次資料: [ICEGR: An Intent-Coherent End-to-End Generative Retrieval Framework for E-commerce Search](https://arxiv.org/pdf/2608.29652v1)、arXiv v1。2026-09-22確認。PDF SHA-256: `b58ae102b84c0215671d3b02b33c904aebb99fe270ff48c5fc5e48d35d95cdd3`。取得済みPDFは `/tmp/research-2026-09-22/2608.29652v1.pdf` を再利用した。

| 原典 | Lab | 省略 |
| --- | --- | --- |
| Eqs. 2–3 | propagate | click log、8B encoder |
| Eqs. 4–8 | method | fusion・量子化・合成query生成 |
| Eq. 9 | beta_factor | DPO optimizer・reference policy |
| §3.3 SRA/BPR | relevance gateの人工例 | 正式pair選定規則の全再現 |
| Tables 2,5 | Evidence | neural学習・A/B再現なし |

公式コード: 確認したPDFに本手法の公開実装へのリンクは見つからなかった。公開の有無を網羅的に保証するものではない。

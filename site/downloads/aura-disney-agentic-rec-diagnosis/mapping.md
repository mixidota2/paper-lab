# Original Paper / Official Code Mapping

一次資料: [AURA: Agentic Diagnosis and Refinement for Production Recommender Systems at Scale](https://arxiv.org/pdf/2609.16625v1)、arXiv v1。2026-09-22確認。PDF SHA-256: `069c7aa504d2881a293c4d083dc2603a11b55dba53f2fb6f40dae64cc8ae317e`。取得済みPDFは `/tmp/research-2026-09-22/2609.16625v1.pdf` を再利用した。

| 原典 | Lab | 省略 |
| --- | --- | --- |
| §3.3 | select | LLM分類・集約とsample分析 |
| §3.6 | validate | JSON schema・import検証、DB |
| Table 1 | rubric表 | judge再実行 |
| §4.2 / Table 3 | holdの説明用gate | 本番ranker、公式gateの再現ではない |
| Table 5 | 費用の母集団・推定範囲 | token使用量追試 |

公式コード: 確認したPDFに本手法の公開実装へのリンクは見つからなかった。公開の有無を網羅的に保証するものではない。

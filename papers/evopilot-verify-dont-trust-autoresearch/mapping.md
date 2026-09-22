# Original Paper / Official Code Mapping

一次資料: [Verify, Don’t Trust: Agentic Model Development for Video Discovery Retrieval at Scale](https://arxiv.org/pdf/2609.21257v1)、arXiv v1。2026-09-22確認。PDF SHA-256: `5f1e410fd37a0188628871d4cd241ab3bf8dcd4af0dfae1043f1c82aec90f913`。取得済みPDFは `/tmp/research-2026-09-22/2609.21257v1.pdf` を再利用した。

| 原典 | Lab | 省略 |
| --- | --- | --- |
| §3 P/K | evaluate | ANN・two-tower・head |
| Eq. 3 / §4.2 | verify + human_review pending | remote attestation・人間判断 |
| §5.2 / Table 5 | fault mutation | 原典10 fixtureの全再現 |
| §5.3 / Table 6 | incident timeline | 学習比較の再実行 |
| §5.4 | online evidence | guardrail欠落、product A/B未追試 |

公式コード: 確認したPDFに本手法の公開実装へのリンクは見つからなかった。公開の有無を網羅的に保証するものではない。

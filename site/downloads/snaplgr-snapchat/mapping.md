# Original Paper / Official Code Mapping

一次資料: [LLM-Based Generative Retrieval for Snapchat Content Recommendation](https://arxiv.org/html/2607.28895v3)。本文・実験・限界・付録を確認（2026-09-21）。キャッシュは `/tmp/research-2026-09-21/2607.28895.html`。HTML SHA-256: `e48dfa317ab605269c7ae5ba58dd653508e1da4af545044c29f1826363fdd139`。

| 原典 | Labの対応 | 意図した省略・境界 |
| --- | --- | --- |
| §2.1 / Appendix A.1 | SID・PPR解説 | モデル学習を省略 |
| §2.2 / Table 2 | CPT/SFT・RSA図 | Qwenの再学習なし |
| Fig. 2 / Appendix A.3 | materialize | max-valueへ簡略化、候補budget省略 |
| Tables 6–8 | serving表・Evidence | throughputとonline liftを分離 |

公式コード: 確認した本文に、このシステムの学習・配信を再実行できる公開実装へのリンクは見つからなかった。公開の有無を網羅的に調べたという意味ではない。

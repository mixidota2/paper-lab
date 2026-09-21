# Original Paper / Official Code Mapping

一次資料: [PushDualGen: Enabling LLMs to Generate Semantic IDs with Interpretable Copy for Industrial Push Recommendation](https://arxiv.org/html/2608.07989v1)。本文・実験・限界・付録を確認（2026-09-21）。キャッシュは `/tmp/research-2026-09-21/2608.07989.html`。HTML SHA-256: `d9b5a6a513a106135d568004ffd4adcc31579c92052b59ab6da94388839fe89c`。

| 原典 | Labの対応 | 意図した省略・境界 |
| --- | --- | --- |
| Fig. 1 / Appendix A | 8 slot × 512の解説 | Omni学習と量子化は省略 |
| Eqs. 4–6 | decode / skip切替 | 有限頻度モデル。説明の忠実性は未検証 |
| Eq. 7 | rank(beta) | 全探索内積。ANN・実user特徴は省略 |
| Tables 1–2 | Evidence | 15%は計、各群15%ではない |

公式コード: 確認した本文に、このシステムの学習・配信を再実行できる公開実装へのリンクは見つからなかった。公開の有無を網羅的に調べたという意味ではない。

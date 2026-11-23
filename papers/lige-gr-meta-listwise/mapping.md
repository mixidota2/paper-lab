# Original Paper / Official Code Mapping

一次資料: [LIGE-GR: A Smooth Leap from Ranking to Generative Recommendation in the LLM Era](https://arxiv.org/html/2609.18148v1)。本文・実験・限界・付録を確認（2026-09-21）。キャッシュは `/tmp/research-2026-09-21/2609.18148.html`。HTML SHA-256: `fdef5a1acc124ad2687d95b0964e4c27ab599f62ffdc1568f5f5131b5513ed7f`。

| 原典 | Labの対応 | 省略した処理・確認できる範囲 |
| --- | --- | --- |
| Fig. 3 / §3.1 | CA/CFの解説 | Transformer学習は省略 |
| Eqs. 9–14 / Algorithm 1 | score / future / decode | CAの予測値は人工的に設定し、CLには説明用の規則を使う |
| Algorithm 2 / §4.3 | timeout / trimmed_top3 | 実際の経過時間は測らず、GPUや配信環境も使わない |
| Tables 2–4 | Evidence | 論文が報告した値。Labが実行して得た値ではない |

公式コード: 確認した本文に、このシステムの学習・配信を再実行できる公開実装へのリンクは見つからなかった。公開の有無を網羅的に調べたという意味ではない。

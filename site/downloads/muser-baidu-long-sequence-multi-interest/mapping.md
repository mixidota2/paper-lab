# 原論文と最小実装の対応

[一次PDF v1](https://arxiv.org/pdf/2609.23677v1)。確認日：2026-09-23。保存済みPDFを再利用した。

SHA-256: `a7e0d31274719fc0da9c38d70d7529707930773b6ee304336b0aa2c72bc4c195`

| 原論文 | 最小コード / 図 | 省略 |
| --- | --- | --- |
| Fig. 2 / Eq. 6 | `compress()`、token予算図 | attentive pooling、learned embedding |
| Eq. 12 | `orthogonal_penalty()` | next-K training |
| Eq. 14 / §III | 非同期融合の説明 | Redis/Kafka、実QPS制御 |
| Fig. 4a | 著者値の棒図 | recall追試 |

Fig. 5のL꜀=1,000は特定の区間設定での結果。全長・境界が変われば再計算が必要。

公式コード：確認した一次PDF・arXiv書誌に、この方式の再現用リポジトリを特定できる案内はなかった。非公開であるとの断定はしない。

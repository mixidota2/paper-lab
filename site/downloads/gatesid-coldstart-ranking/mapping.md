# Original Paper / Official Code Mapping

確認日：2026-09-17。一次PDF：[2603.22916v2.pdf](https://arxiv.org/pdf/2603.22916v2)。arXiv初回日：2026/03/24、確認版の日付：2026/07/09。

SHA-256：`7b0100bbcba779768f491bfd2ee809c224a7ba3e8db5bb640dca057fdaa9f208`

保存先：`/workspace/research-bot/tmp-scout/2026-09-17/2603.22916v2.pdf`。既存HTMLを発見用に使い、上記の版を固定したPDF本文・関連する表と付録で照合した。図はこのLabで作った説明図で、元論文の画像コピーではない。

| 原論文の箇所 | 確認対象 | Labと省略範囲 |
| --- | --- | --- |
| §3.1、式1–2、§4.1.3 | RQ-VAE 4×256とranking構成 | method.md。量子化学習は未実装 |
| §3.2、式4–8、Algorithm 1 | GFSAの共有attention | run.py: gfsa / softmax |
| §3.3、式9–11 | GRCAのgate付きInfoNCE | run.py: info_nce / compute |
| §4.2・4.8、表1–5 | cohort、ablation、online結果 | Evidence。新商品と全体の分母を分離 |

## 公式コード

確認した論文本文・arXiv書誌には取得可能な公式実装の案内を確認できなかった。非公開であると断定せず、公式コードの独立実行はNOT TESTEDとする。

## 独立再現の境界

RQ-VAE学習、maturity gate学習、CTR/CTCVRのranking学習、AUC、online GMV、5ms制約はNOT TESTED。固定gateでの凸結合を確認しただけで、本番のcold-start改善を検証したわけではない。

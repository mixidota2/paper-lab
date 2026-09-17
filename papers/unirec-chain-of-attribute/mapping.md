# Original Paper / Official Code Mapping

確認日：2026-09-17。一次PDF：[2604.12234v4.pdf](https://arxiv.org/pdf/2604.12234v4)。arXiv初回日：2026/04/14、確認版の日付：2026/04/30。

SHA-256：`338c6b948306f69053f4dd5b0fbff1c5f7440c2ec22d0ba4f1d9e4dbed19da78`

保存先：`/workspace/research-bot/tmp-scout/2026-09-17/2604.12234v4.pdf`。既存HTMLを発見用に使い、上記の版を固定したPDF本文・関連する表と付録で照合した。図はこのLabで作った説明図で、元論文の画像コピーではない。

| 原論文の箇所 | 確認対象 | Labと省略範囲 |
| --- | --- | --- |
| §3.2、式1–2、Algorithm 1、図2 | 露出capacityとprefix集中 | run.py: capacity_repair。固定中心・1層へ簡略化 |
| §3.3、式3–6、表2 | Bayes、CoA、entropy | run.py: entropy / compute。分母の反例はLab独自 |
| §3.4–3.6、式7–28 | CDC、cross-attention、RFT+DPO | method.md。モデル・学習は省略 |
| §4.1–4.2、表1・3・5 | offline比較と面別A/B | Evidence。online段削除の詳細は不明 |

## 公式コード

確認した論文本文・arXiv書誌には取得可能な公式実装の案内を確認できなかった。非公開であると断定せず、公式コードの独立実行はNOT TESTEDとする。

## 独立再現の境界

属性予測の誤り、full training、beam recall、RFT/DPOの学習、Shopee A/B、段ごとの削除効果はNOT TESTED。entropyの減少だけからCTR上昇や生成・判別の同値性を結論しない。

# Original Paper / Official Code Mapping

確認日：2026-09-17。一次PDF：[2606.31031v2.pdf](https://arxiv.org/pdf/2606.31031v2)。arXiv初回日：2026/06/30、確認版の日付：2026/08/01。

SHA-256：`98bd7a0c0b96943c794450e1883397c6318c6bdcf02b9fedc868516a1561847f`

保存先：`/workspace/research-bot/tmp-scout/2026-09-17/2606.31031v2.pdf`。既存HTMLを発見用に使い、上記の版を固定したPDF本文・関連する表と付録で照合した。図はこのLabで作った説明図で、元論文の画像コピーではない。

| 原論文の箇所 | 確認対象 | Labと省略範囲 |
| --- | --- | --- |
| §2・図1、§4 | prompt/pageのtoken化、約200Mのモデル | method.md、prompt図。tokenizerの実装は省略 |
| §5.1–3・表1 | NTP / WBC / Dr. GRPOの区別 | method.md。学習・報酬モデルは未実装 |
| §6.3–4 | 業務mask、hybrid row decode | run.py: decode / score |
| §8・図6 | 候補集合、14日A/B、CI、遅延 | Evidenceと最終CI図。オンライン再現なし |

## 公式コード

確認した論文本文・arXiv書誌には取得可能な公式実装の案内を確認できなかった。非公開であると断定せず、公式コードの独立実行はNOT TESTEDとする。

## 独立再現の境界

Netflixデータ、reward system、200Mモデルの学習、ページ満足度、RLのオンライン効果、Gryphonとの実験比較はNOT TESTED。人工例でhybridと全逐次が一致しても、任意の相互作用で一致する保証はない。

# Original Paper / Official Code Mapping

確認日：2026-09-17。一次PDF：[2609.02730v1.pdf](https://arxiv.org/pdf/2609.02730v1)。arXiv初回日：2026/09/02、確認版の日付：2026/09/02。

SHA-256：`e5a796ede0b8653df5c58f7e8ab6a5cfa7e165afb60c34df2d216a952b65aae2`

保存先：`/workspace/research-bot/tmp-scout/2026-09-17/2609.02730v1.pdf`。既存HTMLを発見用に使い、上記の版を固定したPDF本文・関連する表と付録で照合した。図はこのLabで作った説明図で、元論文の画像コピーではない。

| 原論文の箇所 | 確認対象 | Labと省略範囲 |
| --- | --- | --- |
| §3、式1–2 | 非定常制約付き設定最適化 | method.md。regret計測は未実装 |
| §4.1–4.3、図1、Appendix A・図2・表3 | 記憶、bounded proposal、数値optimizer | run.py: project / discrete。LLMは手作り提案へ置換 |
| §5.1、表1 | video R1–R3とcohort | Evidence・round比較表 |
| §5.2、§6・式3・表2 | 節約額44%増、推定token費用 | run.py: compute。金額は人工例 |

## 公式コード

確認した論文本文・arXiv書誌には取得可能な公式実装の案内を確認できなかった。非公開であると断定せず、公式コードの独立実行はNOT TESTEDとする。

## 独立再現の境界

LLM推論、attribution、人の監督の削減、時系列のpolicy改善、online A/B、実際のserving costはNOT TESTED。予算射影が成功しても、目的関数Jの改善は確認していない。

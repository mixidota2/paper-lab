# Original Paper / Official Code Mapping

確認日：2026-09-17。一次PDF：[2606.26859v2.pdf](https://arxiv.org/pdf/2606.26859v2)。arXiv初回日：2026/06/25、確認版の日付：2026/06/26。

SHA-256：`637fd4c1c9737acc05db71095cb15f9ef05d9402b0f97601194b8dbb0abba97f`

保存先：`/workspace/research-bot/tmp-scout/2026-09-17/2606.26859v2.pdf`。既存HTMLを発見用に使い、上記の版を固定したPDF本文・関連する表と付録で照合した。図はこのLabで作った説明図で、元論文の画像コピーではない。

| 原論文の箇所 | 確認対象 | Labと省略範囲 |
| --- | --- | --- |
| §4–5 | Brainstorm / Developingの契約 | method.md。LLMとrepository操作は未実装 |
| §6.3–6.4 | KEEP / EXTEND / DISCARD、負結果の記憶 | run.py: judge。入力済みCIと人工threshold |
| §7.1、式7–9 | SGPOの局所変更とpaired replay | run.py: admit。rubric評価は手作り |
| §8、表5–8、式10 | 374案funnel、worker-week比較 | Evidenceとfunnel図。観察比較として記載 |

## 公式コード

確認した論文本文・arXiv書誌には取得可能な公式実装の案内を確認できなかった。非公開であると断定せず、公式コードの独立実行はNOT TESTEDとする。

## 独立再現の境界

LLMによる発案・coding、統計推定器、production rollout、SGPOの改善率、workerのスケーリング、人間との同条件比較はNOT TESTED。guardrail recordの計算は機構の一部だけである。

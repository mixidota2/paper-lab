# Original Paper / Official Code Mapping

確認日：2026-09-17。一次PDF：[2607.10044v1.pdf](https://arxiv.org/pdf/2607.10044v1)。arXiv初回日：2026/07/10、確認版の日付：2026/07/10。

SHA-256：`7baccbd83b1733289df30310e9fa2e0b877b69eaf7464b2b40bc9bbaeb042d19`

保存先：`/workspace/research-bot/tmp-scout/2026-09-17/2607.10044v1.pdf`。既存HTMLを発見用に使い、上記の版を固定したPDF本文・関連する表と付録で照合した。図はこのLabで作った説明図で、元論文の画像コピーではない。

| 原論文の箇所 | 確認対象 | Labと省略範囲 |
| --- | --- | --- |
| §2、Algorithm 1、Appendix D | GPU native beamとchild lookup | run.py: beam。CPUの集合検査へ簡略化 |
| §3・4.1–4.5、表1・6、Appendix E–F | 800M条件、品質とpercentile | 実測点のSLO図。値は論文表から転記 |
| §4.8・表3、Appendix G | online backend/beam変更 | Evidence。backend単独の因果効果ではない |
| Abstract | 公開予定のcode | 査読後公開予定と記載。取得できた公式実装なし |

## 公式コード

本文は査読後公開予定とする。確認した一次資料から取得可能な公式実装は見つからなかった。MARISAは比較対象でありFlashTrie公式実装ではない。

## 独立再現の境界

CUDA、Narrow-LOUDSのメモリ圧縮、800M index、teacher精度、30msのproduction SLO、収益はNOT TESTED。下のSLO操作は著者表の読み替えであり、新しい測定ではない。

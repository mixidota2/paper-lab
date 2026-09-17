# Original Paper / Official Code Mapping

確認日：2026-09-17。一次PDF：[2602.22647v2.pdf](https://arxiv.org/pdf/2602.22647v2)。arXiv初回日：2026/02/26、確認版の日付：2026/07/20。

SHA-256：`1a50773da5416592e35b3dd62e35d81dac91c64e04cc179c3d28bae252ab0bad`

保存先：`/workspace/research-bot/tmp-scout/2026-09-17/2602.22647v2.pdf`。既存HTMLを発見用に使い、上記の版を固定したPDF本文・関連する表と付録で照合した。図はこのLabで作った説明図で、元論文の画像コピーではない。

| 原論文の箇所 | 確認対象 | Labと省略範囲 |
| --- | --- | --- |
| §4.1–4.2、図1 | prefix制約とCSR変換 | run.py: build / walk。dense lookupは省略 |
| §4.3–4.4、Algorithm 1–2、Appendix A | maskとVNTK、beam state更新 | method.md。accelerator kernelは未実装 |
| §5.1–5.4、表1–2、Appendix D | latency条件とonline鮮度 | Evidence・時間の比較図 |
| 公式static_decoding/csr_utils.py、decoding_jax.py、decoding_pt.py | index構築とJAX/PyTorch推論 | 公式コードを参照。Labは依存を持たないCPU模型 |

## 公式コード

公式実装を取得し、READMEとindex/decodingの対応を確認した。commit `ac18fa1870ac45e0a3559090a0ea9ec005226cf5`。JAX/PyTorch実装自体の実行はNOT TESTED。

[公式repository](https://github.com/youtube/static-constraint-decoding)。`static_decoding/csr_utils.py` がindex構築、`decoding_jax.py` / `decoding_pt.py` が推論側。

## 独立再現の境界

TPU/GPU kernel、dense前段、VNTK固定長slice、8-token・20M集合のメモリ、本番freshness更新、遅延、CTRはNOT TESTED。CPUの小さなCSR参照実装から948倍を再現したとは言わない。

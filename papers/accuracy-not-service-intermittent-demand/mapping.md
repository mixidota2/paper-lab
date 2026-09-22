# Original Paper / Official Code Mapping

一次資料: [Accuracy Is Not Service: A Decision-Aware Benchmark for Intermittent-Demand Forecasting](https://arxiv.org/pdf/2609.13840v1)、arXiv v1。2026-09-22確認。PDF SHA-256: `7dc61d06092ef0a22a85ca5896d9432bdf345dc878b03bf81e367799a1d7f70d`。取得済みPDFは `/tmp/research-2026-09-22/2609.13840v1.pdf` を再利用した。

| 原典 / 公開成果物 | Lab | 省略 |
| --- | --- | --- |
| Eqs. 3–4 / §III-D | replay | 4品目・lead=2、価格・platformなし |
| Eqs. 6–7 | normalize | Chronos-2本体、arcsinh |
| §IV-A / industrial_orderbook_38.csv | author-orderbook.csv / rank-scatter.svg | 実注文replayとCI推定 |
| Table V / §IV-D | Evidence / 中心移動図 | 学習・全38手法 |
| 公式 MANIFEST.md | 本文のRUF境界 | RUF v2全実行は未実施 |

公式コードの `src/scripts/10_experiments/run_raf_instancenorm.py` と `run_synthetic_instancenorm.py` が正規化追試の入口。`validate_38_complete.py` は38手法・欠落0・fallback0を確認する。公式README/Manifestを2026-09-22に取得した。

公式公開先: [https://github.com/sfcheng-research/icdm-2026-reproduction](https://github.com/sfcheng-research/icdm-2026-reproduction)。READMEを確認したが、全実験の再実行はしていない。

公式CSV: [industrial_orderbook_38.csv](https://raw.githubusercontent.com/sfcheng-research/icdm-2026-reproduction/main/results_release/industrial_orderbook/industrial_orderbook_38.csv)。取得日2026-09-22、SHA-256 `36cec2e7a4bdaa718ecbd05989ebbc661b1020d0044dfeb8ca4349a05f7b3ff9`。図はこのローカル固定コピーから生成する。

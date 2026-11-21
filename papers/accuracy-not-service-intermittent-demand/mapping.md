# 原論文・公式コードとLabの対応

一次資料：[Accuracy Is Not Service: A Decision-Aware Benchmark for Intermittent-Demand Forecasting](https://arxiv.org/pdf/2609.13840v1)（arXiv v1）。2026-09-22に確認。確認に使ったPDFのSHA-256は `7dc61d06092ef0a22a85ca5896d9432bdf345dc878b03bf81e367799a1d7f70d`。

| 原論文・公開成果物 | Labで扱う箇所 | Labでは扱わないこと |
| --- | --- | --- |
| 式3–4、§III-D | `replay()` で人工注文を順に処理 | 4品目、入荷待ち2期間に縮小。価格やプラットフォームの違いは扱わない |
| 式6–7 | `normalize()` で正規化と逆変換を確認 | Chronos-2本体、arcsinhの処理 |
| §IV-A、`industrial_orderbook_38.csv` | 公開CSVの順位から相関を求め直し、散布図にする | 実注文を使った再実行、信頼区間の推定 |
| 表V、§IV-D | 論文の報告値と正規化の人工例を別々に示す | 学習、全38手法の比較の再実行 |
| 公式 `MANIFEST.md` | 人工の公開データRUFと、非公開の実注文データを区別する | RUF v2を使った実験の全実行 |

[公式リポジトリ](https://github.com/sfcheng-research/icdm-2026-reproduction)のREADMEとManifestは2026-09-22に確認した。正規化の追試に対応するスクリプトは `src/scripts/10_experiments/run_raf_instancenorm.py` と `run_synthetic_instancenorm.py`。`validate_38_complete.py` は38手法の結果に欠落や代替結果（fallback）がないかを確認する。Labでは公式実験の全再実行はしていない。

散布図に使った[公式CSV](https://raw.githubusercontent.com/sfcheng-research/icdm-2026-reproduction/main/results_release/industrial_orderbook/industrial_orderbook_38.csv)は2026-09-22に取得した。SHA-256は `36cec2e7a4bdaa718ecbd05989ebbc661b1020d0044dfeb8ca4349a05f7b3ff9`。Labでは同じ版を `author-orderbook.csv` として固定し、その順位から散布図を作る。

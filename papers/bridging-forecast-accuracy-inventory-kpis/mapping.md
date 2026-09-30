# 原論文・公式コード対応

一次資料は[arXiv v2](https://arxiv.org/pdf/2601.21844v2)と、著者が公開した[IDA_2026](https://github.com/caisr-hh/TruckParts-Demand-Inventory-Simulator/releases/tag/IDA_2026)。リリース先とタグを確認した。公式コードの実行は行っていない。

| 論点 | 原論文 | 公式実装の入口 | このLab |
|---|---|---|---|
| 故障から需要を作る | §3、式1、Figure 1–2 | notebooks/main.ipynbのDemand Generator | method.mdで説明。run.pyでは独立な人工需要へ簡略化 |
| 予測と在庫評価の接続 | §4、Figure 3 | 同ノートのForecasting / Cost Simulation | 共通の在庫規則でZeroとCrostonを比較 |
| 7モデルのMAEと費用 | §5、Table 1、Figure 5 | 同リリースの実験結果 | results.jsonのreportedへ丸め値を転記 |
| 間欠性の分布 | Figure 4 | 需要生成結果 | 分布の点群は再生成していない |
| シナリオ別相関 | Figure 6 | 結果集計 | 全体0.95、シナリオ平均−0.16を説明。相関は再計算していない |

公式リリースのREADMEはStandardInventoryPolicyとIntegratedSimulatorを入口として示す。最小コードはこの実装の移植ではない。車両の故障寿命、季節性、ドリフト、発注費、輸送費、緊急便、バックオーダー処理を省いている。

Table 1のRandom ForestとARIMAの総費用はともに7.5×10⁵、XGBoostとRandom ForestのMAEはともに0.43と丸められている。同値の厳密な順位は断定しない。本文のR²に関する総括と表の正の値にはずれがあるため、本Labはその総括を根拠に使わない。

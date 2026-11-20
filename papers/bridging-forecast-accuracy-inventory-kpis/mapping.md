# 原論文・公開コードと照合する

一次資料は[原論文のv2](https://arxiv.org/pdf/2601.21844v2)と、著者の[公開リリース IDA_2026](https://github.com/caisr-hh/TruckParts-Demand-Inventory-Simulator/releases/tag/IDA_2026)です。リリースのURLとタグは確認しましたが、公開コードは実行していません。

| 知りたいこと | 原論文 | 公開コードの入口 | Labで確認できること |
|---|---|---|---|
| 部品の故障から需要を作る手順 | §3、式1、Figure 1–2 | `notebooks/main.ipynb` のDemand Generator | `method.md` で説明。Labのコードでは、日ごとに独立した人工需要に置き換えた |
| 予測結果から在庫費用を計算する手順 | §4、Figure 3 | 同じノートのForecasting / Cost Simulation | 同じ補充ルールでZeroとCrostonを比較 |
| 7モデルの予測誤差と費用 | §5、Table 1、Figure 5 | 同じリリースの実験結果 | 丸めた報告値を `results.json` の `reported` に転記 |
| 需要が発生する頻度や数量のばらつき | Figure 4 | 需要生成結果 | 図の点群は再生成していない |
| 全体とシナリオ内での順位相関 | Figure 6 | 結果集計 | 著者報告の全体0.95、シナリオ平均−0.16を説明。相関は再計算していない |

公開リリースのREADMEは `StandardInventoryPolicy` と `IntegratedSimulator` を実装の入口に挙げています。Labの小実験は、著者のコードを移植したものではありません。車両部品の故障までの寿命、季節性、時間とともに変わる需要、発注費、輸送費、緊急便、未納分の繰り越しを省いています。

Table 1では、Random ForestとARIMAの総費用はともに7.5×10⁵、XGBoostとRandom ForestのMAEはともに0.43と丸めて表示されています。この数字だけで同値のモデル同士に順位は付けません。また、本文の決定係数（R²）についての総括と、表にある正の値が食い違うため、Labではその総括を根拠に使っていません。

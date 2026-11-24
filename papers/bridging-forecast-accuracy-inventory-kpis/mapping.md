# 原論文・公開コードと照合する

この対応表の一次資料は[原論文のv2](https://arxiv.org/pdf/2601.21844v2)と、著者の[公開リリース IDA_2026](https://github.com/caisr-hh/TruckParts-Demand-Inventory-Simulator/releases/tag/IDA_2026)です。既存の確認記録にリリースのURLとタグがあります。Labは著者のコードを実行していません。

| 知りたいこと | 原論文 | 公開コードの入口 | Labで確認できること |
|---|---|---|---|
| 著者が故障から需要を作る方法 | §3、式1、Figure 1–2 | `notebooks/main.ipynb` のDemand Generator | `method.md` で手順を説明する。Labは日ごとに独立した人工需要を使う |
| 著者が予測から在庫費用を計算する方法 | §4、Figure 3 | 同じノートのForecasting / Cost Simulation | Labは同じ補充ルールでZeroとCrostonを比べる |
| 7モデルの予測誤差と費用 | §5、Table 1、Figure 5 | 同じリリースの実験結果 | 著者が丸めて示した値を `results.json` の `reported` に記録した |
| 需要の発生頻度と発生日の数量のばらつき | Figure 4 | 需要生成結果 | Labは図の点群を再生成していない |
| 全体で求めた順位相関と、条件内で求めた順位相関 | Figure 6 | 結果集計 | 著者報告の全体0.95、シナリオ平均−0.16を説明する。Labは相関を再計算していない |

著者のリリースのREADMEは、`StandardInventoryPolicy` と `IntegratedSimulator` を実装の入口に挙げています。Labはそれらを移植せず、別の小実験を作りました。車両部品が故障するまでの寿命、季節性、時間につれて変わる需要はモデル化していません。発注費、輸送費、緊急便、未納分の繰り越しも省いています。

Table 1の表示では、Random ForestとARIMAの総費用はともに7.5×10⁵、XGBoostとRandom ForestのMAEはともに0.43です。いずれも丸めた値なので、表示が同じモデルに優劣は付けません。また、著者の本文にある決定係数（R²）の総括は、表の正の値と食い違います。Labはこの総括を根拠に使っていません。

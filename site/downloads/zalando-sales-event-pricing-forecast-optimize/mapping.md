# 原論文と最小実装の対応

一次資料は[High-frequency pricing at scale for e-commerce v1](https://arxiv.org/pdf/2606.13741v1)。提供PDF全14ページを読了した。SHA-256はlab.yamlに記録する。本文に公式実装URLの記載は見当たらず、公式コードの実行はしていない。

| 原論文 | 本Lab | 境界 |
|---|---|---|
| Fig. 3、§3.1、Table 1 | LightGBM、割引グリッド、単調制約 | 市場別・予測日別モデルは共通の小モデルへ縮約 |
| 式(1)、Fig. 4 | run.pyのmain、αの21候補 | 架空3商品。全離散Pareto解は列挙しない |
| 式(3)〜(7) | financial() | R、VAT、C、γを固定。γを週次モデルから推定しない |
| 式(12)、§4.1 | experiment()の定弾力性と対数正規ノイズ | 100週の在庫消化ヒューリスティックは省略。56日で学習 |
| §4.2、Table 3 | 同じ特徴のMSE/Tweedieを最適化へ接続 | 価格をランダムに割付。既知弾力性を入力。実現は期待需要 |
| Table 2、p.9 | results.jsonのpaper_evidence.table2 | 主要3モデルの平均値。標準偏差を図では省略 |
| Table 3、p.10 | paper_evidence.table3 | PCIIのoracle比。著者のシミュレーションであり実地A/Bではない |
| Table 4–5、pp.11 | paper_evidence.table5と統合効果図 | 23試験の統合値。波別の効果や区間は復元しない |

著者報告の表と最小実験の数値はresults.jsonで別キーに保存する。paper_lab/zalando05.pyはそれを描画するだけで、HTMLを原本にしない。損失関数の変更だけで実地の因果効果が得られるとは主張しない。

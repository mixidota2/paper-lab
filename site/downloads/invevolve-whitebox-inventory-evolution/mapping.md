# 原論文と最小実装の対応

一次資料は [InvEvolve v4](https://arxiv.org/pdf/2605.00369v4)、2026年6月5日版。提供PDFを本文・付録まで読んだ。公式実装のURLは本文から確認できず、このLabは独立した学習用実装である。

| 原論文 | Labの対応 | 省略・変更 |
| --- | --- | --- |
| §2、Fig. 2、Eqs. 5–9 | `run.py` の共通需要replay、改善平均、Hoeffding半径 | 方策提案・champion更新を省略。ξ=0の説明用判定 |
| §4、Appendix C | READMEのGLM-4.7-Flash / GRPO説明 | 学習・SlimeRL・生成コードの実行を省略 |
| §5.1、Table 2 | `results.json` の `paper_reported.synthetic` | 著者集計の転記。30 workspaceを再実行していない |
| §5.2、Table 3、Appendix H | CJの勝率と潜在需要復元の注意 | CJ取得、復元精度、A3C/E2Eを未検証 |
| §5.3.2、Fig. 5、Table 6 | `order()` と対話的な発注応答図 | 固定係数。96条件のOptuna探索を省略 |
| Appendices E–F | 理論保証と実用校正の区別 | シフト予算とblockwise t半径を実装していない |

発注応答図は論文式から生成する。整数不足では Kp=1 のTilted-PICがTilted-CBSに一致する。連続不足では丸めが入るため、両式が常に等しいとは主張しない。線で結んだ点の間は補助表示である。

# 一次資料と最小実装の対応

[原論文 v1](https://arxiv.org/pdf/2602.22685v1)について、2026-09-29に保存済みのPDFとarXivの版情報を確認した。

PDF SHA-256: `0ea7569ce0136f13c710a18caeee577e4b308c62df7ad7102bfa7e2ceb52dff7`

| 原典 | Labで読めるもの | Labで試していないこと |
| --- | --- | --- |
| Figure 1, Eqs. (2)–(3) | 振り分け器の勾配をどう計算するかを示すSTEの演算図 | encoderの学習 |
| Eqs. (8)–(14) | `nb()` と `hurdle()` による需要量の確率計算 | decoderの実装と学習損失の計算 |
| Figures 4–5 | 需要の区分ごとにどのexpertへ振り分けたかを示す表 | 学習後の振り分けの追試 |
| Table 4 | M5で著者が報告した予測精度の棒グラフ | M5でのモデルの訓練と精度評価 |

関連Lab：[Accuracy Is Not Service](https://mixidota2.github.io/paper-lab/papers/accuracy-not-service-intermittent-demand.html)。予測精度だけから在庫サービス水準を判断できない理由を扱う。

確認したPDFとarXivの概要ページでは、著者提供のリポジトリへの案内を見つけられなかった。公開コードが存在しないとは断定できない。`run.py` はLabが説明用に作った実装である。

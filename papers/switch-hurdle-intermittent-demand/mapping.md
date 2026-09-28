# 一次資料と最小実装の対応

[原論文 v1](https://arxiv.org/pdf/2602.22685v1)。2026-09-29に保存済みPDFとarXivの版情報を確認。

PDF SHA-256: `0ea7569ce0136f13c710a18caeee577e4b308c62df7ad7102bfa7e2ceb52dff7`

| 原典 | 最小実装・図 | 省略 |
| --- | --- | --- |
| Figure 1, Eqs. (2)–(3) | STEの演算図 | encoder学習 |
| Eqs. (8)–(14) | nb(), hurdle() | decoderと学習損失 |
| Figures 4–5 | 条件別routing表 | routingの追試 |
| Table 4 | M5精度の棒グラフ | M5の訓練・評価 |

関連Lab：[Accuracy Is Not Service](https://mixidota2.github.io/paper-lab/papers/accuracy-not-service-intermittent-demand.html)。精度からサービス水準を推測しないために併読する。

公式コード：確認したPDFとarXiv概要ページに著者提供リポジトリの記載を見つけられなかった。公開コードが存在しないとの断定ではない。run.pyはこのLab独自の説明用実装。

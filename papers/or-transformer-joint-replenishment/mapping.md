# 一次資料と最小実装の対応

[原論文 v2](https://arxiv.org/pdf/2609.01933v2)。2026-09-29に保存済みPDFとarXivの版情報を確認。

PDF SHA-256: `429e579b4a3e66987056f90231cedb72543336b36b56317efcc070c8e3a9fb2b`

| 原典 | 最小実装・図 | 省略 |
| --- | --- | --- |
| Figure 3.1, Eq. (2) | attention()・token図 | 多層・多head・学習 |
| Appendix C.3 | cost(), derivative()と差分照合 | critic・長いrollout |
| Table D.5 | 規模別の費用表 | 訓練と評価episode |
| Figure 4.1 | 8意思決定の比較図 | Gurobi実行・時間計測 |

公式コード：確認したPDFとarXiv概要ページに著者提供リポジトリの記載を見つけられなかった。公開コードが存在しないとの断定ではない。run.pyはこのLab独自の説明用実装。

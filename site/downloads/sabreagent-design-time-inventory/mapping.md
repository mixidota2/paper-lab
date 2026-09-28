# 一次資料と最小実装の対応

[原論文 v2](https://arxiv.org/pdf/2609.19760v2)。2026-09-29に保存済みPDFとarXivの版情報を確認。

PDF SHA-256: `4ba27bba95dd74380118e7339e447fd81b7ff627953e5e943a29380072bd3308`

| 原典 | 最小実装・図 | 省略 |
| --- | --- | --- |
| Figures 1–2 | 設計時と運用時の二段図 | LLMの実行 |
| Eq. (1), Proposition 8 | project()と在庫の追跡表 | 需要予測の推定 |
| Theorem 1, Appendix B | dp_check() | 一般証明・非定常需要 |
| Eq. (4) | capped()と発注曲線 | rolloutによるθ,c選択 |
| Table 1 / Figure 4 / Table 2 | NR比較・本文 | ベンチマークの再実行 |

公式コード：確認したPDFとarXiv概要ページに著者提供リポジトリの記載を見つけられなかった。公開コードが存在しないとの断定ではない。run.pyはこのLab独自の説明用実装。

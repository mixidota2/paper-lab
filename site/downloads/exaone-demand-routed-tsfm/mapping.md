# 原論文との対応

原典：[EXAONE Demand 1.0, v1](https://arxiv.org/pdf/2609.30880v1)、2026-09-25。ローカルPDF全23ページ（本文・参考文献・付録）をpdftotextで確認した。

| 原典 | このLab | 一致と省略 |
| --- | --- | --- |
| §4.1 式1–2、p.9 | run.py `stats` | 相対閾値、ADI、非ゼロCV²。欠測処理は省略 |
| §4.1 式3–4、Table 6 | READMEの8統計量説明 | 学習routerは実装しない |
| §4.2 式5–6、Table 7 | `membership`、操作平面 | τa=0.35、τc=0.60。ゼロCV²は数値安定化用に1e−12へclip |
| §4.3 式7–10、Figs.8,10–11 | 平面のπ・π̃比較 | T=0.5。表示する教師比率は学習済みqではない |
| §4.4 式11–12、Fig.9、Table 10 | LoRA模式図 | 凍結W₀、共有rank16、専門rank4。行列学習は省略 |
| §3、Table 5、Fig.7 | 欠品操作図 | 潜在量と観測量を分離する説明用決定的系列。負の二項・Bass・共食いは省略 |
| §5.1 式13 | 古典法のMASE比較 | 人工系列のm=1、算術平均。論文の22データセット幾何平均とは別 |
| Tables 8–9 | results.jsonのreported_*、色付き比較表 | Table 9の全22行、EXAONE/Synthetic/TiRex/Chronosの4列を転記 |
| Appendix B | READMEの先行研究 | 2005年分類、Moirai-MoE、Chronos-2、TiRexとの設計上の違い |

[公式コード](https://github.com/LGAI-Research/EXAONE-Forecast)・[モデル](https://huggingface.co/LG-AI-Research/EXAONE-Demand-1.0)は原典記載URL。公式コードの実行、ファイル単位の照合、重みの取得はNOT TESTED。対応する実装箇所を推測で断定していない。

人工比較のクラス→古典法割当、Gamma数量生成、検証用系列による共通手法選択はLab独自。論文の性能再現に数えない。

| 原論文の場所 | Labの対応 | 実装の範囲 |
| --- | --- | --- |
| Figure 1、Appendix C | 3方式の比較 | 推論入力と出力採点の境界を図示 |
| 式3–4、Appendix B | 行動指示probe | `instruction_probe()` は頻度モデルのみ |
| 式5–7 | 軌跡選択 | `reward()`、8本の人工rollout |
| 式8–13、Algorithm 1 | entropy routingと損失 | `gates()`、`losses()`。SFT・勾配学習なし |
| Table 6 | 面別A/B | 著者報告値。独立再現なし |
| Table 8 | 強制指示の表 | 原論文値。toyと別表示 |

[全文v1](https://arxiv.org/html/2607.24255v1)を本文からAppendix Hまで確認した。公式コードは原論文・arXiv書誌で未確認。`run.py`はこのLab独自の教材で、公式実装ではない。

出典上の留保：§5のoffline 3BとG.2の0.7B、Table 10のdefaultとTable 3の最良教師は区別した。Table 6をabstractのGMV範囲で置き換えない。v1からのシステム更新であり、サービス全体のカスケード撤去を確認した資料としては使わない。

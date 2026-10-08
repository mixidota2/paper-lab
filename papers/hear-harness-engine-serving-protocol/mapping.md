# 原論文と最小実験の対応

一次資料：[arXiv 2610.06597v1](https://arxiv.org/pdf/2610.06597v1)。2026-10-08照合。PDF SHA-256: `ecdc8cdbeb1f3e93579141278a920ac9009f737785373af5a6694d2c122d3d0c`。

| 原典 | Lab | 境界 |
| --- | --- | --- |
| Table 1–2 / Fig.2 | 通信図 | 4方向の意味と受理/完了の違いを段階表示。wire formatの実装ではない。 |
| §4.2 / Appendix A.2 | schedule() | hot優先と待機保護を単一スロットで縮約。全prefix一致のtoy。 |
| Table 3–6 | lab.yaml / results.jsonのpaper | SCBenchとMooncakeを別の系列で保存。独立再現ではない。 |
| Eq.4–5 / Appendix A.1 | method節 | 6構成の役割別選択を説明。GPU/KVモードの実装は省略。 |

公式コード：[著者がPDFで案内した公開先](https://anonymous.4open.science/r/hear-3D1E/)。本Labはこのコードを実行・監査していない。

匿名公開先は今回の取得で内容を確認できなかった。コード内の関数や固定revisionとの対応はNOT TESTEDとする。

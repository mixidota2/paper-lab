# 原論文と最小実験の対応

一次資料：[arXiv 2610.06992v1](https://arxiv.org/pdf/2610.06992v1)（2026-10-08照合）。PDF SHA-256: `52bf7be5914f36c1682f8979591fd491498267c5e1908917621b823be4260b31`。

| 原論文の箇所 | Labで読む・試す場所 | どこまで対応するか |
| --- | --- | --- |
| Fig.1 / §5 | `experiment(actions)` | 信号制御の点検手順のうち、将来情報で選択が変わるかを1期間の補充問題で検算した。交通制御器は再現していない。 |
| Table 2–3 / Fig.4 | `lab.yaml` と `results.json` の `paper` | MAE、区間に実績が入った割合、対応bootstrapの信頼区間は著者の結果を転記した。 |
| §5.3–5.5 | READMEと手法の節 | 判断時点の修正、64行動の全探索、比例配分と先着順の差を説明した。人工実験には含めていない。 |

[著者がPDFで案内した公開コード](https://github.com/ljnvs/traffic)のREADMEで、`code/run_control_corrected_rollout_v8.py` が最終制御の入口、`config/SPLIT.json` が日付分割、`results/` が集計結果だと確認した。コード自体の実行や監査はしていない。原車両記録、抽出道路網、日別flowは公開物に含まれず、原論文の実験には別途必要になる。

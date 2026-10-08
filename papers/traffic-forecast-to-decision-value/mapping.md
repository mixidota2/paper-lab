# 原論文と最小実験の対応

一次資料：[arXiv 2610.06992v1](https://arxiv.org/pdf/2610.06992v1)。2026-10-08照合。PDF SHA-256: `52bf7be5914f36c1682f8979591fd491498267c5e1908917621b823be4260b31`。

| 原典 | Lab | 境界 |
| --- | --- | --- |
| Fig.1 / §5 | experiment(actions) | 関門を1期間の補充選択へ縮約。交通制御の再実装ではない。 |
| Table 2–3 / Fig.4 | lab.yaml / results.jsonのpaper | MAE、被覆率、対応bootstrap CIの転記。 |
| §5.3–5.5 | README / method節 | 時刻修正、64行動全探索、内部比例配分とFIFOのずれを説明。toyでは省略。 |

公式コード：[著者がPDFで案内した公開先](https://github.com/ljnvs/traffic)。本Labはこのコードを実行・監査していない。

公開READMEで `code/run_control_corrected_rollout_v8.py` が最終制御の入口、`config/SPLIT.json` が日付分割、`results/` が集計結果であることを確認した。原車両記録、抽出道路網、日別flowは公開物に含まれず、toyから本実験へ移る際は別途必要となる。

# 一次資料と自作実装の対応

- [arXiv v1 HTML](https://arxiv.org/html/2611.08252v1)：§§1〜7、Tables1〜5、Appendix Aのseed別表と図1〜5のキャプションを読解。今回の実装担当は全PDF画素を監査していません。
- §3.3・§4.1 → run.pyのorigins/fit/select/evaluate。原著の情報分離を説明する独立toyであり、公式CVやニューラルモデルの再現ではありません。
- §5 Table3 → table3.json。公表済み丸め値を転記し、表示行平均・勝数・Weather感度を自作集計。掲載平均は別配列に保持しています。
- [公式実装](https://github.com/vcerqueira/experiments-tscv)のsrc/config.pyを読解。読取時treeは3ba404c160ff9e59bd554fc7bd0352f7497434eb。SEED456、N_FOLDS5、N_SAMPLES20、OUT_SET_MULTIPLIER2、STEP_SIZE1、HOLDOUT_FOR_OUTSET0。既定は主設定の30%除外にならず切替が必要です。論文対応commitは未固定、公式全実装・Q=0処理は未監査、コードは実行していません。
- model.jsは自作の表示用計算、interactive.jsは分割図・条件切替・reset・JSON保存。Python版との数値照合と、最終testを変える変形検査を行います。原PDF・第三者コード・管理記録は配布しません。

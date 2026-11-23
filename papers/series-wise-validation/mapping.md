# 一次資料とLabの実装を照合した範囲

- [arXiv v1 HTML](https://arxiv.org/html/2611.08252v1)：§§1〜7、Tables1〜5、Appendix Aのseed別の表、図1〜5のキャプションを読みました。今回の実装ではPDFの全ページを画像として確認したわけではありません。
- §3.3・§4.1に対応するのはrun.pyのorigins/fit/select/evaluateです。学習や選択に使うデータと最終評価を分ける仕組みを示すLab独自の合成例で、公式のCV手順やニューラルモデルを再現するものではありません。
- §5 Table3の丸め済みの公表値をtable3.jsonに転記しました。表示した行の平均と勝数、Weatherを外したときの変化はLabで計算します。論文に掲載された平均は別の配列に保持しています。
- [公式実装](https://github.com/vcerqueira/experiments-tscv)のsrc/config.pyを読みました。参照時のtreeは3ba404c160ff9e59bd554fc7bd0352f7497434eb、設定はSEED456、N_FOLDS5、N_SAMPLES20、OUT_SET_MULTIPLIER2、STEP_SIZE1、HOLDOUT_FOR_OUTSET0です。既定のままでは論文の主設定である30%の系列除外にならず、切り替えが必要です。論文の再現に使うcommitとしては固定していません。公式実装の全体とQ=0の場合の処理は未確認で、コードは実行していません。
- model.jsは表示に使うLab独自の計算を担当し、interactive.jsは分割図、条件の切り替え、初期値へのリセット、JSON保存を担当します。Python版と数値を比べ、最終テストのデータを変えてもモデル選択に影響しないことを検査します。原PDF、第三者コード、管理記録は配布しません。

# 原典と実装の対応

- [arXiv v1](https://arxiv.org/abs/2610.25170v1)、[PDF](https://arxiv.org/pdf/2610.25170v1)：§3/Table1、§4/Figure2・Eq.3–4、§5/Eq.7、§6.1、§6.9/Tables11–12、§9をWeb抽出本文で確認。全補足・全図の画素監査は未了。
- [公式snapshot](https://github.com/karthik-iyer-au/retail-world-models/tree/b7c182730a7744ce655fb467af36b951baca629a)：第三者コードは読解のみ。学習・推論は未実行。
- `scripts/category_cost_uncertainty.py`、blob `28cbd341087dab7d6e655dd40022d5309e995ea3`：訂正式、窓別計算後の平均、窓前単位数が非正なら単価0。`run.py:metrics/windows`は自作の小規模有理数計算であり、コードの転載ではない。
- `results/paper1_revision/tables/category_cost.csv`、blob `bd62596c0581216210a75dc32882085447b0633e`：`variant=dollars`のみを`table_winners`で検算。
- `results/paper1_revision/tables/decisions.csv`、blob `ff166093fdb687d9ad44f8a50424482fba16d04c`：`set=rolling`かつ`decision=replenish_0.8`のみ。`category_planning`は旧式なので不使用。
- `model.js`は自作の表示用計算、`interactive.js`は入力検査・再計算・reset。`run.py`は独立した有理数の検算。`results.json`は自作例だけ。

一次資料・公式コードには著者の利用条件があります。本配布物にPDF・第三者コード・生データを同梱しません。結果の勝数は公表値からの限定集計で、原実験再現とは区別します。

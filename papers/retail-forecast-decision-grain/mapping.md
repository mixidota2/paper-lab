# 著者の資料と、Labが計算した範囲

Labは[初版の書誌](https://arxiv.org/abs/2610.25170v1)と[初版のPDF](https://arxiv.org/pdf/2610.25170v1)を確認した。PDFでは表1、図2、式3〜4・7、§6.1、§6.9と§9を読んだ。[著者の公開リポジトリの対象版](https://github.com/karthik-iyer-au/retail-world-models/tree/b7c182730a7744ce655fb467af36b951baca629a)では、訂正後の計算式と費用の表を確認した。著者モデルは学習・実行しておらず、補足全体や図の細部までは照合していない。

[第3版の書誌](https://arxiv.org/abs/2610.25170v3)と[本文](https://arxiv.org/html/2610.25170v3)については、表8・13・14を中心に、著者が比較した方式と数値を確認した。Labが費用を数えた表は初版に対応する。第3版の結果を元データや著者のコードから計算し直してはいない。

| 初版の著者リポジトリにある資料 | Labが確かめたこと |
| --- | --- |
| `scripts/category_cost_uncertainty.py`（blob `28cbd341087dab7d6e655dd40022d5309e995ea3`） | 訂正式を評価期間ごとに計算し、その比率を平均する。評価より前の販売数量が0以下なら単価を0とする。教材は `run.py` の `metrics` と `windows` で、それぞれの手順を小さな例として示す。 |
| `results/paper1_revision/tables/category_cost.csv`（blob `bd62596c0581216210a75dc32882085447b0633e`） | Labは `variant=dollars` の行だけを取り出し、 `table_winners` で訂正後の計画費用が最小の方式を数えた。 |
| `results/paper1_revision/tables/decisions.csv`（blob `ff166093fdb687d9ad44f8a50424482fba16d04c`） | 発注損失は `set=rolling` かつ `decision=replenish_0.8` の行から数えた。旧式の `category_planning` はこの集計には入れていない。 |

Labが行ったのは、著者が公表した表から最小値を数えることと、人工例で評価式を計算することである。モデルの学習や元データからの予測を再現したものではない。配布物には論文PDF、著者のコードや生データを含めていない。

## 配布ファイルに入っているもの

- `model.js` は、画面に入力した値から誤差と発注損失を計算する。
- `interactive.js` は入力を検証し、条件を変えたときに表示を更新する。保存と復元、初期値に戻す操作も扱う。
- `run.py` は、Pythonの分数計算を使って画面とは別に数値を検算する。
- `results.json` は教材の人工例の値だけを収録する。

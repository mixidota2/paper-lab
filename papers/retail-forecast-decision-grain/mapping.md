# 論文のどの箇所に、Labの計算が対応するか

## Labが照合した資料

[arXiv v1](https://arxiv.org/abs/2610.25170v1)と[PDF](https://arxiv.org/pdf/2610.25170v1)では、Webで抽出できた本文を使って、§3の表1、§4の図2・式3〜4、§5の式7、§6.1、§6.9の表11〜12、§9を確認しました。補足全体と全図の画素は確認していません。[著者の公開リポジトリの確認対象版](https://github.com/karthik-iyer-au/retail-world-models/tree/b7c182730a7744ce655fb467af36b951baca629a)のコードは読みましたが、著者モデルの学習や推論は実行していません。

[arXiv v3](https://arxiv.org/abs/2610.25170v3)は、[本文](https://arxiv.org/html/2610.25170v3)の表8・13・14を中心に確認しました。Labの費用の再集計はv1に対応します。v3の数値は本文で著者の報告として紹介し、著者の元データやコードでは再計算していません。

## 初版の費用をどの表から数えたか

| 著者が公開したファイル | Labが確認したこと |
| --- | --- |
| `scripts/category_cost_uncertainty.py`（blob `28cbd341087dab7d6e655dd40022d5309e995ea3`） | 著者のコードは、訂正式を評価期間ごとに計算してから平均します。評価より前の販売数量が正でない場合は単価を0にします。Labの `run.py:metrics/windows` は、その手順を人工例で説明するために、有理数で計算します。 |
| `results/paper1_revision/tables/category_cost.csv`（blob `bd62596c0581216210a75dc32882085447b0633e`） | Labは `variant=dollars` の行だけを使い、`table_winners` で費用が最小だった回数を数えました。 |
| `results/paper1_revision/tables/decisions.csv`（blob `ff166093fdb687d9ad44f8a50424482fba16d04c`） | Labは `set=rolling` かつ `decision=replenish_0.8` の行だけを使いました。旧式の `category_planning` は除きました。 |

Labは著者が公表した表で最小値を数えました。予測モデルを動かして原実験を再現したわけではありません。論文や著者コードにはそれぞれ利用条件があり、Labの配布物にはPDF・第三者コード・生データを同梱していません。

## Labのファイルで確かめられること

- `model.js` は画面に表示する値を計算します。
- `interactive.js` は入力を検証し、画面を再計算したり初期値に戻したりします。
- `run.py` は有理数を使い、画面と別の実装で人工例を検算します。
- `results.json` は人工例の結果だけを収録しています。

# 論文・公開結果表と、Lab教材の対応

## どこを読んだか

[arXiv v1](https://arxiv.org/abs/2610.25170v1)と[PDF](https://arxiv.org/pdf/2610.25170v1)について、Webで抽出した本文から §3/Table1、§4/Figure2・Eq.3–4、§5/Eq.7、§6.1、§6.9/Tables11–12、§9 を確認しました。補足全体や全ての図の画素は確認していません。[著者の公開リポジトリの確認対象版](https://github.com/karthik-iyer-au/retail-world-models/tree/b7c182730a7744ce655fb467af36b951baca629a)のコードは読みましたが、著者モデルの学習や推論は実行していません。

## 何を計算し、どの公表値を数え直したか

| 著者リポジトリのファイル | 読み取ったこと、Labで確かめたこと |
| --- | --- |
| `scripts/category_cost_uncertainty.py`（blob `28cbd341087dab7d6e655dd40022d5309e995ea3`） | 訂正式を評価期間ごとに計算してから平均すること、評価より前の販売数量が正でない場合に単価を0とすることを確認しました。Labの `run.py:metrics/windows` は、小さな説明例を有理数で計算する自作コードです。 |
| `results/paper1_revision/tables/category_cost.csv`（blob `bd62596c0581216210a75dc32882085447b0633e`） | `variant=dollars` の行だけを使い、`table_winners` で最小費用だった回数を数え直しました。 |
| `results/paper1_revision/tables/decisions.csv`（blob `ff166093fdb687d9ad44f8a50424482fba16d04c`） | `set=rolling` かつ `decision=replenish_0.8` の行だけを使いました。`category_planning` は旧式なので対象外です。 |

著者の表から公表値が最小だった回数を数えたもので、原実験の再現ではありません。一次資料や公式コードには著者の利用条件があります。この配布物にはPDF・第三者コード・生データを同梱しません。

## Labのファイルは何をするか

- `model.js` は画面に表示する値を計算します。
- `interactive.js` は画面の入力を検証し、再計算や初期値へのリセットを行います。
- `run.py` は有理数を使い、画面の計算とは独立して検算します。
- `results.json` に入っているのは自作例の値だけです。

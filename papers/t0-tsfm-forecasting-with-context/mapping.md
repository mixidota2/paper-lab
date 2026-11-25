# 論文・公式コード・Lab小実験の対応

このLabは[一次PDF v1](https://arxiv.org/pdf/2609.24559v1)に基づきます。既存の調査では2026年9月23日に保存した39ページのPDFから全文を抽出し、§5.1.2の評価、Table 5、§6の限界まで確認しました。保存されたPDFのSHA-256は `e23720637cc9e2409620d5ecc7658fe57d0c897dd53814a75f933a7a6dff5757` です。

| 論文の箇所 | Labで扱う範囲 | 固定コミットの参照先 |
| --- | --- | --- |
| §4.1・Eq. 2：標準化に使う情報の範囲 | 図で予測時点の前後を区別します。標準化は再実装していません。 | `t0/scaler.py`：`CausalScaler`、`_compute_causal_stats`、`_compute_global_stats` |
| Fig. 3：変数間で情報を読む向き | `propagate()` で人工例の依存関係だけを追います。 | `t0/model/layers/group_attention.py`：`VariateSelfAttention`、`t0/mask.py` |
| §4.1：分位点の出力 | `ordered_quantiles()` で、分位点が逆転しないことを確認します。 | `t0/model/layers/head.py`（参照先。実行なし） |
| Table 5：補助変数を渡す場合と渡さない場合 | 図で著者の成績を表示し、`skill_audit()` で丸め済みの値から差を計算します。 | 公式モデルでは計算し直していません。 |

既存調査では[標準化](https://github.com/theforecastingcompany/tfc-t0/blob/a2eca8d80892485c44679c638bcd883ae974f751/t0/scaler.py)と[変数方向のattention](https://github.com/theforecastingcompany/tfc-t0/blob/a2eca8d80892485c44679c638bcd883ae974f751/t0/model/layers/group_attention.py)をコミット `a2eca8d80892485c44679c638bcd883ae974f751` で読みました。[公式リポジトリ](https://github.com/theforecastingcompany/tfc-t0)の公開APIは `T0Forecaster.from_pretrained()` と `predict(..., future_covariates=...)` です。Labはモデルの重みをダウンロードせず、公式コードで予測していません。

## 論文の参照制限は、既存調査で読んだ経路では確認できなかった

論文§4.1では、将来の値が分かる変数zが予測対象を参照できないようにします。既存調査で確認した固定コミットの経路では、`MaskBuilder.build_group_mask()` がグループIDの一致とパディングの条件を作り、`Transformer.forward()` がそれを変数方向のattentionに渡していました。その経路からは、論文が説明する変数の役割別の制限までは確認できませんでした。一方、将来の値が分かる変数が時間方向に前後を読む設定と、各時点までの値で標準化する処理は確認できました。

これは固定コミットを読んだ範囲での記録で、学習済みモデルから未来情報が漏れたという実験結果ではありません。実際の挙動を判断するには、モデルの版、学習時のコード、入力の作り方も確認する必要があります。[固定コミットのマスク](https://github.com/theforecastingcompany/tfc-t0/blob/a2eca8d80892485c44679c638bcd883ae974f751/t0/mask.py#L31)・[呼び出し側](https://github.com/theforecastingcompany/tfc-t0/blob/a2eca8d80892485c44679c638bcd883ae974f751/t0/model/layers/transformer.py#L169)

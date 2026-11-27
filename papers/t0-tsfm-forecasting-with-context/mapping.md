## 論文の記述、公開コードの確認記録、Labの計算を分ける

一次資料は[原論文PDF v1](https://arxiv.org/pdf/2609.24559v1)です。以前の照合では、2026年9月23日に保存した39ページのPDFで、第5.1.2節、表5、第6節を確認しました。そのPDFのSHA-256は `e23720637cc9e2409620d5ecc7658fe57d0c897dd53814a75f933a7a6dff5757` です。

| 原論文 | Labで確かめる範囲 | 以前の確認で読んだコード |
| --- | --- | --- |
| 第4.1節・式2 | 図で、標準化が予測時点の前後にあるどの値を使うかを示します。処理は再実装していません。 | `t0/scaler.py` の `CausalScaler`、`_compute_causal_stats`、`_compute_global_stats` |
| 図3 | `propagate()` で、二時点の人工例における情報の伝わる方向を追います。 | `t0/model/layers/group_attention.py` の `VariateSelfAttention` と `t0/mask.py` |
| 第4.1節の分位点 | `ordered_quantiles()` で、小さい分位点に正の差を足すと順序が保たれることを確認します。 | `t0/model/layers/head.py`。実行はしていません。 |
| 表5 | `skill_audit()` で、著者らの丸め済みの報告値から差を計算します。 | 公式モデルで計算し直していません。 |

以前の確認で読んだ版は、コミット `a2eca8d80892485c44679c638bcd883ae974f751` の[標準化](https://github.com/theforecastingcompany/tfc-t0/blob/a2eca8d80892485c44679c638bcd883ae974f751/t0/scaler.py)と[変数間の注意](https://github.com/theforecastingcompany/tfc-t0/blob/a2eca8d80892485c44679c638bcd883ae974f751/t0/model/layers/group_attention.py)です。既存の確認記録は、[公開リポジトリ](https://github.com/theforecastingcompany/tfc-t0)の呼び出し方を `T0Forecaster.from_pretrained()` と `predict(..., future_covariates=...)` と記録しています。Labは公式モデルの重みを取得せず、予測も実行していません。

### 論文どおりの変数の参照制限は、読んだコードからは確認できなかった

原論文は、将来分が既知の変数zが予測対象の実績を読まないようにします。以前のコード確認では、`MaskBuilder.build_group_mask()` が、グループIDが一致するかと、パディングかどうかで、参照可能な場所を決めていました。`Transformer.forward()` はこのマスクを変数方向の注意に渡していました。この経路では、どの変数が予測対象かに応じた論文の制限は確認できませんでした。一方、既知の変数が時間方向に前後を読む処理と、その時点までの値で標準化する処理は、以前の調査で確認しています。[固定版のマスク](https://github.com/theforecastingcompany/tfc-t0/blob/a2eca8d80892485c44679c638bcd883ae974f751/t0/mask.py#L31)・[呼び出し側](https://github.com/theforecastingcompany/tfc-t0/blob/a2eca8d80892485c44679c638bcd883ae974f751/t0/model/layers/transformer.py#L169)。

この記録は、固定した版の該当箇所を読んだ範囲に限ります。学習済みモデルから未来の実績が漏れたことを示す実験結果ではありません。その有無を判断するには、モデルの版、訓練時の処理、予測時に作る入力を合わせて確かめる必要があります。

# 原論文と最小実装の対応

[一次PDF v1](https://arxiv.org/pdf/2609.24559v1)。確認日：2026-09-23。保存済みPDFを再利用した。

SHA-256: `e23720637cc9e2409620d5ecc7658fe57d0c897dd53814a75f933a7a6dff5757`

| 原論文 | Lab | 公式コード（固定commit） |
| --- | --- | --- |
| §4.1 causal scaling / Eq. 2 | cutoff図。scalerは再実装しない | `t0/scaler.py`: `CausalScaler`, `_compute_causal_stats`, `_compute_global_stats` |
| Fig. 3 / asymmetric variate attention | `propagate()`で依存だけ計算 | `t0/model/layers/group_attention.py`: `VariateSelfAttention`、`t0/mask.py` |
| §4.1 quantile decoder | `ordered_quantiles()` | `t0/model/layers/head.py`（対応先、実行せず） |
| Table 5 | `skill_audit()`と入切表示 | 論文の丸め済み集計値を監査 |

公式repo確認commit：`a2eca8d80892485c44679c638bcd883ae974f751`（2026-09-23）。[固定版scaler](https://github.com/theforecastingcompany/tfc-t0/blob/a2eca8d80892485c44679c638bcd883ae974f751/t0/scaler.py)と[attention](https://github.com/theforecastingcompany/tfc-t0/blob/a2eca8d80892485c44679c638bcd883ae974f751/t0/model/layers/group_attention.py)を静的に確認。公開APIは `T0Forecaster.from_pretrained()` / `predict(..., future_covariates=...)`。重みをdownloadせず、予測品質を検証したとはしない。

保存済みtxtはPDFの10ページ目で途切れていたため、同じ39ページPDFから全文を再抽出し、§5.1.2、Table 5、§6まで確認した。

公式コード：[著者が案内する公開先](https://github.com/theforecastingcompany/tfc-t0)。本Labは公式モデルを実行していない。

## 論文と確認したコードの差

固定commitの `MaskBuilder.build_group_mask()` はgroup ID一致とpaddingの条件を作り、`Transformer.forward()` はそれをそのままvariate attentionへ渡す。確認した経路では、論文§4.1の「既知未来zはtargetを逆参照しない」というrole別制限を見つけられなかった。時間方向のfuture双方向maskとcausal scalerは確認できる。これは静的な不一致の記録であり、学習済みcheckpointでの未来情報漏洩を実証したものではない。モデル版・学習時コード・入力構築を含む追加監査が必要。

[maskの固定版](https://github.com/theforecastingcompany/tfc-t0/blob/a2eca8d80892485c44679c638bcd883ae974f751/t0/mask.py#L31) / [呼出側](https://github.com/theforecastingcompany/tfc-t0/blob/a2eca8d80892485c44679c638bcd883ae974f751/t0/model/layers/transformer.py#L169)。

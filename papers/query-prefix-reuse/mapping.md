| 一次箇所 | 教材 | 確認範囲と省略 |
|---|---|---|
| §3 Eq.3、§4 Fig.2 | method.md、処理図 | query共有と履歴依存を説明。Tₜの実測・深さからのms推定はしない |
| §4.2–4.4 | run.py/model.jsのtoy | 手作りprefixと整数score。ReuseCut/CellPlan/PathKDの学習は未実装 |
| §4.5、Appendix C | l4_scored/branches/admitted | 採点後の採用だけを模す。OPD/GRPOとset-dependent policyは未実装。原著d=3は枝を削らない |
| Table 1、Eq.21 | 指標切替 | query-macroの掲載3手法。SID単位でありitem回収ではない |
| Table 5、Appendix D | projectionとプリセット | Pの端点補間。Static Q品質は別のpartition実測。P95/P99は補間しない |
| §5.7、Appendix D | 処理図と根拠 | coldは即時E2E、positive-depth missのみ非同期準備。A/B効果の投影はしない |

出典：[arXiv 2611.04259v1](https://arxiv.org/html/2611.04259v1)。ローカルの自作コードを原公式snapshotとして表示しません。原著モデル・ログ・公式コードの実行物はありません。

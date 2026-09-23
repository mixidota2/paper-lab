# 原論文と最小実装の対応

[一次PDF v1](https://arxiv.org/pdf/2607.03362v1)。確認日：2026-09-23。保存済みPDFを再利用した。

SHA-256: `36e81449d940ab105c75bdc7e3806eccdd128bf50de1bfe0b4086890edcc2acb`

| 原論文 | 最小コード / 図 | 省略 |
| --- | --- | --- |
| Eq. 14 Chained-MTP | `token_probs()` | FFN学習、beam、8192語彙 |
| §3.2.2 mixed SID | `retrieve()`、二経路図 | author alignment、RQ-Kmeans/SimVQ |
| Eqs. 20–24 | 報酬とGSISPOの数式説明 | RL training、zero-std処理 |
| §3.4 | rankerへ接続 | 本番quota、重複規則は非再現 |
| Table 6 | p値を含む表 | A/B再現、差分間の検定 |


公式コード：確認した一次PDF・arXiv書誌に、この方式の再現用リポジトリを特定できる案内はなかった。非公開であるとの断定はしない。

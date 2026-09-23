# 原論文と最小実装の対応

[一次PDF v1](https://arxiv.org/pdf/2609.23718v1)。確認日：2026-09-23。保存済みPDFを再利用した。

SHA-256: `d25cf755a606caab016178c6f2f5f5122b1d75ad646448c3257a984efe08b508`

| 原論文 | 最小コード / 表示 | 省略 |
| --- | --- | --- |
| Eqs. 7–11 | `assign()` / 距離図 | EMA学習、DSSM、zero-frequency処理 |
| Eq. 15 | `attention()` / 依存表 | learned Q/K/V、multihead、3層 |
| Eqs. 20–25 | methodのloss説明 | trainingを実行しない |
| §3.7 / §4.4 | 配信段階とcode容量 | GPU、index、cache |
| Tables 3–6 | 引用表・ablation棒図 | 著者値、追試値ではない |

関連Labへの比較は読書上の解釈。同条件の性能比較ではない。

公式コード：確認した一次PDF・arXiv書誌に、この方式の再現用リポジトリを特定できる案内はなかった。非公開であるとの断定はしない。

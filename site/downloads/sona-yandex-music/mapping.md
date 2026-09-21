# Original Paper / Official Code Mapping

一次資料: [Sona Technical Report](https://arxiv.org/html/2608.11015v2)。本文・実験・限界・付録を確認（2026-09-21）。キャッシュは `/tmp/research-2026-09-21/2608.11015.html`。HTML SHA-256: `023ab189b8f8f192cb2fcb2040cfc6d7e302ccb4efcbcd97b4148cc4cbc7376e`。

| 原典 | Labの対応 | 意図した省略・境界 |
| --- | --- | --- |
| Fig. 3.2 / §3.3 | history図・attention_pair_counts | 実FLOPsとレイテンシーは未計測 |
| §4.2 | train / teacher | 線形代理、NTP・二headを省略 |
| Tables 7.8–7.12 | 実験1–5の段階図 | 別実験の差は因果効果ではない |
| §8 | 未検証事項 | 全流量・長期・coverageは未解決 |

公式コード: 確認した本文に、このシステムの学習・配信を再実行できる公開実装へのリンクは見つからなかった。公開の有無を網羅的に調べたという意味ではない。

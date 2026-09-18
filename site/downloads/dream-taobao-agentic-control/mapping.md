# 原論文・公式コード対応

一次資料：[2608.09408v3](https://arxiv.org/pdf/2608.09408v3)。確認日：2026-09-18。PDF SHA-256：`aa7c9bfe3ce9cc28ceb03854a5390a5ed268e5bffd166857e6827ce44e55319a`。

| 論文の箇所 | このLab | 最小コード / 省略 |
| --- | --- | --- |
| §3、表1、図3–5 | intent階層・funnel | neural推論は省略。通過率は著者報告 |
| §4.1、式5–14 | 頻度制御の目的と閾値 | invoke。scoreと容量は人工値 |
| §4.2、表6、式16–19、図7 | control plane・override UI | compile_strategy。限定schema・TTL・重みはLab設定 |
| §4.3、式20–25、図8 | Reward Dual Loop | replay_reward。同点境界だけ確認。service callなし |
| §5.1・表7 | 累積lift比較 | compute内の算術。因果推定や有意差検定なし |
| 付録B・表11 | 4B replay-RLのproxy結果 | 学習・評価なし |

M3をLLMの自由出力として描かない。§4.1式13の3項と4項の表記不整合を明記し、欠けた信号を発明しない。全体8.7%・F2約15%・4B routing約6.3%は母集団を区別する。

公式コード：一次PDFと書誌で案内を確認できず、取得・実行はNOT TESTED。run.pyは説明のための独立実装。PDFは指定cacheに1回取得し、本文抽出を再利用した。

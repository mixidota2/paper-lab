# 原論文と最小実装の対応

[一次PDF v1](https://arxiv.org/pdf/2609.17391v1)。確認日：2026-09-23。保存済みPDFを再利用した。

SHA-256: `a68ed302b06ee51087ca6b501a80bf748d073ae2f8c9aef29b8d89a5a15862af`

| 原論文 | 最小コード / 表示 | 省略 |
| --- | --- | --- |
| Algorithm 1 / §4.2 | `decide()`、採択gate図 | LLM、profiling、code mutation、replay |
| §4.2 correctness | artificial `correct` flag | dtype別の数値誤差、business KPI |
| §4.2 noise floor | 6%閾値、再測定要求 | baseline反復・8倍測定 |
| Table 1 | 全体throughputの棒図 | 生のload-test trace |
| Table 3 | 940→約1,500 RPSの引用 | feature serviceの再現 |
| Table 4 | Model Bの250/271 msを明記 | 食い違いの原因は未確認 |

本文のC++変更は[公式Triton issue #8348](https://github.com/triton-inference-server/server/issues/8348)を参照する。これはFlashVector全体の公開コードではない。

公式コード：確認した一次PDF・arXiv書誌に、この方式の再現用リポジトリを特定できる案内はなかった。非公開であるとの断定はしない。

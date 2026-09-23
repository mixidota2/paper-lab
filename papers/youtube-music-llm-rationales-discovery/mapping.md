# 原論文と最小実装の対応

[一次PDF v1](https://arxiv.org/pdf/2609.23877v1)。確認日：2026-09-23。保存済みPDFを再利用した。

SHA-256: `8bd6fc1384ffc394bbd28a9c2d25c8323b5332163d70c520a90c5c78fb5d34db`

| 原論文 | 最小コード / 図 | 省略 |
| --- | --- | --- |
| §3.1 lazy generation | `serve()`のcold fallback | 非同期job基盤 |
| §3.4 KG / familiarity | `canonicalize()` | 実KG、LLM、安全性分類器 |
| §4.3 holdback | 理由だけを外す`serve()`、実験設計表 | 利用者行動と効果量 |

このコードは仕組みの境界だけを示す。非公開clickを合成して因果効果を主張しない。

公式コード：確認した一次PDF・arXiv書誌に、この方式の再現用リポジトリを特定できる案内はなかった。非公開であるとの断定はしない。

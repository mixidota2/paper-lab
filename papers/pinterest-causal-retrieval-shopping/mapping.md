| 原論文 | Lab | 省略した範囲・読み方 |
| --- | --- | --- |
| Fig. 1 / §3.2 | CG gate と Holdout の図 | 実サービスと特徴量の処理は実装していない。 |
| Eq. 7 | run.py dr() | Eq. 8で行う補正値の切り詰めは省いた。 |
| Algorithm 1 / §3.4 | evaluate() | 高速な閾値探索に代え、ログと行動が一致した行を直接選ぶ。 |
| Table 4 | offline / online 比較表 | baseline modelのSV方策の結果を示す。 |
| Table 5 / §4 | Evidence | 最大85%削減と報告された別の実験群とは分けて読む。 |

一次資料: [arXiv 2607.14161v2](https://arxiv.org/abs/2607.14161v2)。PDF SHA-256: `f75332d8051e50bf03cd46c4571f5699ebfd69512501b11204d891c19c71c6d6`。

提供PDFでは公式コードの公開先を確認できませんでした。公開実装がないという意味ではありません。

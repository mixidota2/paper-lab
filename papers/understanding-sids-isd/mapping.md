| 論点 | 一次資料 | Labの対応 | 意図した差 |
| --- | --- | --- | --- |
| SIDの3役・近傍の変化 | [§2–3・表1–2](https://arxiv.org/html/2607.24995) | method.md・geometry.svg | 図は概念、実embeddingでない |
| prefix支援・最終ordering | [式(15)–(17)](https://arxiv.org/html/2607.24995) | run.pyのdecode・数式図 | 8アイテムの固定確率 |
| 支援ranker | [§5.1](https://arxiv.org/html/2607.24995) | ranker | toyは遷移頻度だけ。式(14)の再現ではない |
| 残存率 | [式(10)](https://arxiv.org/html/2607.24995) | evaluate・beam.svg | toyは全9例。top-k条件付きではない |
| 段階別効果 | [表5](https://arxiv.org/html/2607.24995) | 4つの介入と逆順位の比較 | データ・cutoffが異なる |

2026-09-07 UTCにarXiv v1のabs・HTMLを確認。公式実装との行単位照合は未実施。AbstractのIdentity@1=99.57と表1のSentence-T5=99.51の集計対応は確認できないため、精度を1値へ丸めて統合しない。

関連：[GLIDE](glide-spotify-sid.html)は本番R-KMeansと衝突解決、[TGR](tgr.html)は生成候補経路。SID診断のAmazon条件とは区別する。

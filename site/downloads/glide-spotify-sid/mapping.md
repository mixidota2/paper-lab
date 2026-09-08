| 論点 | 一次資料 | Labでの対応 | 省略 |
| --- | --- | --- | --- |
| 残差量子化・long/short | [§4.1–4.3](https://arxiv.org/html/2603.17540) | method.md・数式図・conditioning.svg | モデル学習全体 |
| 経路の追加と衝突 | [§4.4・§5.3](https://arxiv.org/html/2603.17540) | cascade.svg・run.pyのchannel_case | 実ranker・衝突の測定 |
| 入力枠 | [§4.1.1–4.1.2](https://arxiv.org/html/2603.17540) | token_budget | 情報保持・時間測定 |
| 量子化比較とA/B | [表2・§5.3](https://arxiv.org/html/2603.17540) | quantizers.svg・ab-design.svg | 独立再現 |

一次資料は2026-09-07 UTCにabsとHTMLのv1を確認した。正式タイトルと著者名はabsのAuthors欄を採用。公式コードの実体は未確認で、コードの行単位対応はない。非公開ログ、CF重み、encoderの重み、運用費用の詳細は検証不能。図はresearch_botによる教育用の再構成。

関連：[TGR](tgr.html)の追加候補経路、[Metaの検索設計](case-against-generation-retrieval.html)、[SIDのフィルタ診断](understanding-sids-isd.html)。これらの本番条件を同一とみなした比較は行っていない。

# 原論文・公式コード対応

一次資料：[2608.17613v1](https://arxiv.org/pdf/2608.17613v1)。確認日：2026-09-18。PDF SHA-256：`b570cccdb371d4bc1fe7249338b7c449cade0ffe78218482daf7d9f6100c5db2`。

| 論文の箇所 | このLab | 最小コード / 省略 |
| --- | --- | --- |
| 図2、式2–7、付録4、表9 | TUSID融合図・CAW式 | sketch / confidence / fuse。SASRec、射影、量子化の学習は省略 |
| 図1、式8–13、表10 | GL2P・時刻表 | schedule。単位時間・無制限laneというLab仮定 |
| 式15–18、付録5、表8 | 校正切替図 | calibrate / standardize。policy更新なし |
| 表1・3・4、Fig.3 | offline・ablation・throughput | 著者報告値の転記。独立再現なし |
| Online A/B、表10 | 3%・1週間のオンライン結果 | 本番接続なし |

本文のrollout説明と付録5の運用範囲を併記した。実験の報酬はexposure-onlyで、未露出slateの反応を推定したとは読まない。K+Dは同コストstageを仮定した依存深さ。学習・beam幅・GPU資源・通信を含む実測遅延を計算していない。

公式コード：一次PDFと書誌で案内を確認できず、取得・実行はNOT TESTED。run.pyは説明のための独立実装。PDFは指定cacheに1回取得し、本文抽出を再利用した。

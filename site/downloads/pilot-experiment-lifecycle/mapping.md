# 原論文・公式コード対応

一次資料：[2608.18637v1](https://arxiv.org/pdf/2608.18637v1)。確認日：2026-09-18。PDF SHA-256：`43850e56b4c5d51af05899f8d1d927a3bf45720450e700f9c96f377bb9d8ac2c`。

| 論文の箇所 | このLab | 最小コード / 省略 |
| --- | --- | --- |
| §3.1–3.4、図2–3、表2 | lifecycle状態図と権限 | transition。certificateは入力済み。統計engineなし |
| §4.1、図4、式2–3 | PolicyTreeとChampion/Challenger | route / admissible。splitのみの人工例 |
| §5.1–5.2、表5 | draft → supported → approved | memory。独立task数と対立だけ。閾値3はLab仮定 |
| §6、表6–7 | ROAM比較・day 5全bucket | 著者報告を転記。A/B未実行 |
| 表8・§6.3.1 | 計画中の2×2 | NOT TESTED。推定値を置かない |
| 表9・§6.3.2 | Search Efficiency | 8/15、14/15を算術確認 |

本文の最大取引数+0.96%は表7のbucket 25、最大IPV+1.40%はbucket 23。表9の期間内4/5と表7のday 5での3/5を区別した。モデル名と統計実装の欠落を他論文から埋めていない。

公式コード：一次PDFと書誌で案内を確認できず、取得・実行はNOT TESTED。run.pyは説明のための独立実装。PDFは指定cacheに1回取得し、本文抽出を再利用した。

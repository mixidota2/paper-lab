# 原論文・公式コード対応

[一次資料PDF](https://arxiv.org/pdf/2609.27867)。確認箇所：Tables 1, 3, 5–7; Figure 1; §4。保存済みPDFのSHA-256：`5b7b2ed0a545840f48ee7a06cf1a9fc9103bc49e28888195c5f22057c0450a11`。

## 紙面と最小実験の対応

score() → Table 3 / Figure 1の評価粒度を説明する人工例。gap_closed_from_rounded_table6 → Table 6の丸め済み値による算術確認。

Performance / Scaling / Production applicabilityはNOT TESTED。Field Nationの非公開パネル、M5の全手法再評価、区間予測、統計検定は実行していない。店舗の補充費用を最小化する手法も決めていない。

## 公式コードの確認範囲

確認したPDF内で本手法の公式実装URLを特定できなかった。公開実装が存在しないとの断定はしない。公式コードの実行はNOT TESTED。

## 原本と生成物

lab.yamlは本文と図の定義、method.mdは手法説明、run.pyは人工実験、results.jsonは実行結果、mapping.mdは対応表。HTMLはこれらから生成する。PDFの報告値と人工実験値は別に表示する。

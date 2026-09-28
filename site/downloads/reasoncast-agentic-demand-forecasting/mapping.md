# 原論文・公式コード対応

[一次資料PDF](https://arxiv.org/pdf/2608.15291)。確認箇所：Figure 1; §4.2–4.7; Eqs. (6), (8), (11), (12), (16); Tables 2–3。保存済みPDFのSHA-256：`df06b393e718d107e46d56a15547b5187b3fa8731b8a597c0f6aa57b9fd466e6`。

## 紙面と最小実験の対応

correct() → 式(8), (11), (12)の簡略化。wmape() → 式(16)。ルータと潜在表現、学習は省略。

Performance / Scaling / Production applicabilityはNOT TESTED。Chronos-2、Qwen3-32B、検索道具、学習されたルータ、直交射影、GRPOは実行していない。欠品で観測売上が潜在需要を下回る条件、販促費用、在庫サービス水準も未評価。

## 公式コードの確認範囲

確認したPDF内で本手法の公式実装URLを特定できなかった。公開実装が存在しないとの断定はしない。公式コードの実行はNOT TESTED。

## 原本と生成物

lab.yamlは本文と図の定義、method.mdは手法説明、run.pyは人工実験、results.jsonは実行結果、mapping.mdは対応表。HTMLはこれらから生成する。PDFの報告値と人工実験値は別に表示する。

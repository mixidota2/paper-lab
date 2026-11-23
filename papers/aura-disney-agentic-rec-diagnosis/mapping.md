# 原論文・公式コードとLabの対応

一次資料：[AURA: Agentic Diagnosis and Refinement for Production Recommender Systems at Scale](https://arxiv.org/pdf/2609.16625v1)、arXiv v1。確認日は2026-09-22。取得済みのPDFを使った。PDFのSHA-256は `069c7aa504d2881a293c4d083dc2603a11b55dba53f2fb6f40dae64cc8ae317e`。

| 原論文 | Labで対応する箇所 | Labで再現していないこと |
| --- | --- | --- |
| §3.3 | `select` で報告に残す分類を選ぶ | LLMによる分類・集約と、抽出したセッションの分析 |
| §3.6 | `validate` でセッションIDとファイルの参照先が存在するかを確認 | JSON schemaによる検証、インポートの検証、データベース |
| Table 1 | 診断などの出力を評価する基準（rubric）の表 | LLMによる採点の再実行 |
| §4.2 / Table 3 | 修正案を採用せず保留する場合（`hold`）を小実験で説明 | 本番のランキングモデルや、著者が用いた採用判断の再現 |
| Table 5 | 費用の集計に含めた処理と推定の範囲を説明 | トークン使用量を測り直すこと |

確認したPDFには、この手法の公開実装へのリンクが見つからなかった。別の場所に実装が公開されていないことまで確かめたわけではない。

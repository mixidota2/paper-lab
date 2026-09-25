一次資料：[arXiv v1](https://arxiv.org/pdf/2609.27606v1)。確認日：2026-09-25。保存PDFのSHA-256：`9699ce249f7cf0b31394687f95ced4864c4612a622eb59f1d4e3ea9dbb937c99`。

| 原論文 | Lab / 最小コード | 対応と省略 |
| --- | --- | --- |
| §3 / Fig. 1 / Eq. 1–2 | 状態の対応表・式の図 | c1がW2/W3へ渡る依存を保持 |
| §4 / Eq. 3 / Table 6 | freeze_tools() | 2組のみ。streaming、実tool、約50組の全表は省略 |
| §5 / Eq. 4 / Table 7 | ground() | hard conflictのみ。LLM抽出、soft/hint、全段落選択は省略 |
| §6 / Fig. 2 / Appendix E | schedule(), replay() | filter、Bernoulli、重み付き選択、writeback。待機は1ターンへ簡略化 |
| §7 / Table 3–4 / Appendix G | 根拠表・SGA図 | 著者の数値を転記。200セッションの再評価は未実施 |
| §8 / Appendix F | IGPOとの比較 | 転用可能性の解釈。ECでの実験結果ではない |

公式コード：保存済み論文にSGCの実装URLは見当たらない。Appendix G.11はbenchmarkとwrapper schemaの今後の公開を述べる。公開リポジトリの存在を網羅的に調べたわけではなく、公式コードを取得・実行していない。run.pyは独立した説明用実装である。

本文§4とFig. 4 captionのstream区分順序には不一致がある。本文のINTENT→SUB_INTENT→NARRATION→PLANを説明に採用した。Fig. 4は模式図と明記されており、図の時刻から速度を再計算していない。

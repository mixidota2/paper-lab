# 原論文・公式コード対応

[一次資料PDF](https://arxiv.org/pdf/2609.24974)。確認箇所：Figure 1; §3.1–3.3; Eqs. (1), (3)–(5); Tables 2, 4。保存済みPDFのSHA-256：`bf0331faa974d446aa360d7ac8bf9bb0cb44363a4fcebc06aea52c6cfcc8101f`。

## 紙面と最小実験の対応

collect() → 式(3)のPASS/REPLACEと学生可視履歴。nll() → 式(4)の1応答分の算術。重み更新と私的推論maskは省略。

Performance / Scaling / Production applicabilityはNOT TESTED。harness進化、LLMによる点検、推論文のmask、LoRA SFT、28行動の検出、本番配信は実行していない。点検役を外した後の能力保持も人工例では確かめていない。

## 公式コードの確認範囲

論文が示す[公式リポジトリ](https://github.com/metaevo-ai/harness-zero)。今回はコード本体を取得・実行していないため、ファイル単位の一致はNOT TESTED。

## 原本と生成物

lab.yamlは本文と図の定義、method.mdは手法説明、run.pyは人工実験、results.jsonは実行結果、mapping.mdは対応表。HTMLはこれらから生成する。PDFの報告値と人工実験値は別に表示する。

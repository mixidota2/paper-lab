# 原論文・公式コード対応

[一次資料PDF](https://arxiv.org/pdf/2609.28589)。確認箇所：Figures 1–4; Eq. (4); Table 2; §6.3; Table 4。保存済みPDFのSHA-256：`166a1ec87e118921fd9fa2130f7648097df65e9ebcfe096097ea29c0df50f951`。

## 紙面と最小実験の対応

rank() → 式(4)の全候補得点。cache_cost → Figure 2の共有の教育用費用計算。公式のモデル学習・配信コードには対応させていない。

Performance / Scaling / Production applicabilityはNOT TESTED。Transformer、MoE、SNT、学習されたsemantic ID、段階間蒸留、GPUキャッシュ、オンラインA/Bは実行していない。

## 公式コードの確認範囲

確認したPDF内で本手法の公式実装URLを特定できなかった。公開実装が存在しないとの断定はしない。公式コードの実行はNOT TESTED。

## 原本と生成物

lab.yamlは本文と図の定義、method.mdは手法説明、run.pyは人工実験、results.jsonは実行結果、mapping.mdは対応表。HTMLはこれらから生成する。PDFの報告値と人工実験値は別に表示する。

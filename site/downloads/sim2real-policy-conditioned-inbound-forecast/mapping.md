# 原論文と最小実験の対応

一次資料：[arXiv 2610.03662v1](https://arxiv.org/pdf/2610.03662v1)。2026-10-08照合。PDF SHA-256: `cc614acd8402ade5d0931dff42c855f1ece0b03cd098fab50dcff81c559e4a6d`。

| 原典 | Lab | 境界 |
| --- | --- | --- |
| §3.1 Eq.1–2 | rollout() | 商品別の未着注文と在庫保存則。需要・納期を同じseedで再生。 |
| §3.2 Eq.3 / Appendix B | fit(), experiment() | CNNを7特徴の線形回帰に置換。Haar samplerとdual coordinatorは省略。 |
| §3.3 Eq.4 | experiment()の校正ループ | 1週予測の過去観測だけでα,βを更新。多期間共有は省略。 |
| Table 1–3,5,8–9 | lab.yaml / results.jsonのpaper | 著者数値の転記。toyの尺度0.7はTable 1の傾きを再現しない。 |

公式コード：PDFに公開先の案内なし。Labコードは独立した理解用実装である。

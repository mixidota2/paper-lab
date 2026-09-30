# 原論文と最小実装の対応

一次資料は提供された [arXiv v1 PDF](https://arxiv.org/pdf/2603.19621v1)。本文のドラフト日は2026年3月23日、arXiv欄は3月20日である。

| 原論文 | Lab | 検証範囲 |
| --- | --- | --- |
| 導入部pp.3–4：None/Base/Coeff/Both | run.py action()、対話図 | 固定出力の式と逆写像55例 |
| 導入部pp.6–7：正規化と単一方策 | README Method | 本文の説明。学習は省略 |
| §2：欠品需要の外挿 | README Problem | 著者の仮定。推定器は未実装 |
| Fig. 3：Bellman誤差 | Why It Might Work | 著者報告。曲線の再現なし |
| Table 1：DDPG Bothに対する差 | results.json offline、二軸図 | 表を転記。絶対値は復元しない |
| §4：2024年7月DiD、2025年4月反実仮想 | results.json deployment | 選抜対象と推定方法を分けて表示 |
| Table 2：販売量別回転日数 | results.json turnover_by_class | 転記。欠測をnullで保持 |
| §4：全展開・資本費用 | README Evidence | 人民元、対象時点を明記 |

本文掲載の[公式コード](https://github.com/xieyaqi188/DRL_inventory_Alibaba)は未実行。ファイル単位の公式コード対応はNOT TESTED。最小実装は独立した代数計算であり、DDPG、PPO、DS、正規化処理、報酬、需要推定、学習済み重みを省いた。

研究地図のSabreAgent・InvEvolveとの位置づけは本Labの解釈であり、性能の直接比較ではない。

# 論文のどこを、Labでどこまで確かめたか

[原論文のarXiv v1 PDF](https://arxiv.org/pdf/2603.19621v1)を一次資料とします。本文のドラフト日は2026年3月23日、arXiv欄の日付は3月20日です。

| 原論文の箇所 | Labで読める場所 | 確認したこと・していないこと |
| --- | --- | --- |
| 導入部pp.3–4：None、Base、Coeff、Both | `run.py` の `action()` と操作できる図 | ネットワーク出力を固定した式の計算と、発注量を指定して逆算する55例を確認。 |
| 導入部pp.6–7：正規化と単一方策 | READMEのMethod | 販売規模が違う商品で一つの方策を使うための処理を解説。学習は未実行。 |
| §2：欠品した日の需要推定 | READMEのProblem | 欠品時刻から当日の需要を外挿する著者の前提を記載。推定器は未実装。 |
| Fig. 3：Bellman誤差 | Why It Might Work | 著者が報告した価値関数の学習曲線。曲線は再現していない。 |
| Table 1：DDPG Bothを基準にした差 | `results.json` の `offline` と二軸図 | 差を転記。欠品率・回転日数の絶対値は復元していない。 |
| §4：2024年7月の差の差分析、2025年4月のシミュレーション比較 | `results.json` の `deployment` | 対象の選び方と、旧方策との比べ方の違いを説明。 |
| Table 2：販売量別の回転日数 | `results.json` の `turnover_by_class` | 値を転記。欠測は `null` のまま。 |
| §4：対象全体への展開、資本費用の推計 | READMEのEvidenceとOverview | 推計の通貨は人民元。比較と展開の時点を区別。 |

本文が参照する[公式コード](https://github.com/xieyaqi188/DRL_inventory_Alibaba)は実行していません。Labの実装とのファイル単位の照合も **NOT TESTED（未検証）** です。Labは独立した代数計算で、DDPG、PPO、DS、正規化処理、報酬、需要推定、学習済みの重みは含みません。

SabreAgent・InvEvolveとの比較は、何を誰が設計するかを整理するためのLabの解釈です。同じ条件で性能を比較した結果ではありません。

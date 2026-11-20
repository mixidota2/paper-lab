# 原論文のどこを、Labで確かめたか

確認した箇所は§3.1–3.3、図1、Algorithm 1–2、表1・3–6です。

| 原論文 | Labで読めるもの | Labの確認範囲 |
| --- | --- | --- |
| §3.3、式(1)–(3)、Algorithm 2 | `run.py`の`replay()`、補充日数を選ぶ図 | 人工需要2カテゴリ、固定の発注間隔と納期で100候補を全探索。代替需要や実データは扱わない。 |
| 図1、§3.1、表5 | 手法の説明と学習順序の図 | 約93万パラメータのTransformerとVAEの学習は実行していない。 |
| §3.2、Algorithm 1 | `run.py`の`rloo()`、報酬差の式 | 固定報酬4個から基準値を計算しただけ。方策勾配、KLペナルティ、ルールとシミュレーションを合わせた報酬は実装していない。 |
| 表1 | `results.json`の`paper_evidence.offline_total_cost` | 著者の報告値。JDの非公開データは取得していない。 |
| 表3・4、図7 | 現場評価を指標ごとに読む図 | 著者の報告値を、比較基準と単位を分けて表示。対象の対応付け（PSM）や介入前後の差の比較（DiD）は再計算していない。 |

出典は[原論文 2512.19001v2](https://arxiv.org/abs/2512.19001v2)です。確認したPDFで公式コードのリンクは見つけられず、公式実装は実行していません。Labの図は、論文の構造と数値をもとに作ったものです。

[DeepStock](deepstock-policy-regularized-inventory-drl.html)、[SabreAgent](sabreagent-design-time-inventory.html)、[InvEvolve](invevolve-whitebox-inventory-evolution.html)との比較はLabの整理です。個別の手法は各Labの原典対応を参照してください。4手法を同じ条件で直接比較した実験ではありません。

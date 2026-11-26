# 論文の手順のうち、Labで確かめた部分

出典：[原論文2512.19001v2](https://arxiv.org/abs/2512.19001v2)。主に§3の式と手順、図1、表1・3〜6を参照しました。確認したPDFに公式コードへのリンクは見つかりませんでした。Labの図と計算は、原論文の考え方を説明するために作りました。

| 論文の箇所 | Labで読めるもの | Labの確認範囲 |
| --- | --- | --- |
| §3.3、式(1)〜(3)、Algorithm 2 | `run.py` の `replay()` と補充量を選ぶ図 | 2カテゴリの架空の需要で、3日ごとの発注、翌日の入荷を固定し、100候補を列挙する。論文の販売量を使う較正はしない。 |
| 図1、§3.1、§3.4 | 事前学習の順序とモデルの図 | 著者が報告した約93万パラメータはモデルの規模を表す。LabはTransformerやVAEを学習させていない。 |
| §3.2、Algorithm 1 | `run.py` の `rloo()` と報酬差の式 | 4つの報酬を固定し、各候補の報酬をほかの候補の平均と比べる。方策勾配、元の方策から離れすぎないための罰則、ルールとシミュレーションの報酬は実装していない。 |
| 表1 | `results.json` の `paper_evidence.offline_total_cost` | 著者の報告値のうち、JDの現行方式とORPRを記す。非公開データは使っていない。 |
| 表3・4、図7 | 現場比較を指標ごとに読む図 | 比較の種類と原表の単位を分ける。Labは対象の対応付けや、介入前後の差の比較を再計算していない。 |

[DeepStock](deepstock-policy-regularized-inventory-drl.html)、[SabreAgent](sabreagent-design-time-inventory.html)、[InvEvolve](invevolve-whitebox-inventory-evolution.html)とORPRの表は、業務知識をどの段階で使うかを比べたものです。同じ条件で実行して性能を比べたわけではありません。

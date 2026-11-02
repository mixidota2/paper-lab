| 原典の箇所 | このLabでの対応 | 確認範囲 |
| --- | --- | --- |
| §1.1、Theorem 1.1 | method.md、evidence.md | 外生需要・信号、固定納期、完全backlog、同じ情報を使うOPT。全証明は未検証 |
| §2.1〜2.2 | run.py Tree.probability_below / charges / simulate | 単位別条件付き費用と期待値分解。有限木に限定 |
| §3.1〜3.2 | clocks / simulate / cdf | 過去の比率保持、共有ρ、等号停止。recomputedは自作の誤実装比較で原典方策ではない |
| §4.1〜4.2 | 全ラベルの小規模列挙 | 論文の二分探索・oracle呼出し計算量の実装再現ではない |
| §4.3 | tight / 1期間カード | 閉形式を数値評価。小さなεでの極限の例示であり証明ではない |
| 自作の比較基準 | optimum | 有限木の実在庫費用を最小化するDP。未来需要を見ず、履歴ごとに同一行動 |
| 自作表示 | interactive.html / interactive.js、paper_lab/inventory_ct.py | Pythonの出力を選択・描画。no-JS初期表と操作の自動検査、実画面は未確認 |

出典：[Danny Segev, arXiv 2610.41475v1](https://arxiv.org/html/2610.41475v1)。Web本文を独立読解。ローカル原本bytes/hashは未取得。原典表示はCC BY-NC-ND 4.0。著者の図をコピーしていない。

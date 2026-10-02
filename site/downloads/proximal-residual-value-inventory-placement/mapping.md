式(5)–(11)、図1–4、定理1・命題2、表1、付録C.1を確認した。

|一次資料|Labの対応|省略・境界|
|---|---|---|
|図3、付録C.1|run.py: allocate(counterexample)、配置経路の図|2次元の解析解。一般次元の解法なし|
|式(6)–(7)、命題2|allocate(state)、PWL＋二次potential|分離可能な例のみ。密な符号付き結合・学習なし|
|式(5)|allocate(action)|Lab独自の比較例。論文の学習済みbaselineではない|
|式(9)–(10)、定理1|method.md、H⁻¹1=(2,−1)|定理の新しい証明や一般数値検証なし|
|表1・図4・式(11)|paper_evidence、費用棒図、TV|著者値を転記。訓練条件が異なる2実験を分離|
|付録B.2–B.3|手法紹介のみ|State-prox forward/backwardは未実装|

原論文：[2609.23242v1](https://arxiv.org/abs/2609.23242v1)。提供PDFで公式コードのURLを確認できず、公式実装は未実行。図は数式と報告値から独自に作成した。

配置と補充の地図はLabの解釈。[Diff Projection](diff-projection-feasible-multi-echelon-inventory.html)は共有制約を伴う生産・在庫行動、[DeepStock](deepstock-policy-regularized-inventory-drl.html)と[ORPR](orpr-or-guided-pretrain-reinforce-inventory.html)は補充量を扱う。直接の性能比較はない。

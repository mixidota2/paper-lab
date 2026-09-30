|一次資料|最小実装・表示|省いたもの|
|---|---|---|
|§4.1.1 式(2)、図4|run.pyのproject、2変数の射影図|一般次元QP、重みの変更、制約の分解|
|補題1・系1|3例の解析Jacobianと中心差分|右辺bへの微分の実装、活性集合切替点|
|§4.1.2|integer_map、KKTからMᵀλ*=W(z−x*)を算出|NN、HDPO、STEによる学習|
|定義1、図5|x₁+x₂≤2の到達例|完全性定理の証明、一般制約への実験拡張|
|表1・2|lab.yamlの著者報告|小規模最適解・Tempelmeierの再実行|
|表4・5|results.jsonの著者値、費用内訳図|ASMLの学習、費用CDFの再構成|

原論文：[arXiv:2608.02343v1](https://arxiv.org/abs/2608.02343)。提供PDFの§4–6、図3–6、表1–5を確認した。図は数式・平均値から独自に描き直した。公式コードへのリンクは提供PDFで確認できず、公式コードは実行していない。

制約比較はLabの解釈。[Constrained FBSDE](https://mixidota2.github.io/paper-lab/constrained-deep-inventory-fbsde.html)は状態の経路制約を扱う。[DeepStock](https://mixidota2.github.io/paper-lab/deepstock-policy-regularized-inventory-drl.html)は本論文でも引用される。OR-Transformerとの実験比較は行っていない。

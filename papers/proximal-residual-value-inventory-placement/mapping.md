原論文の式(5)–(11)、図1–4、定理1・命題2、表1、付録C.1を確認した。

|一次資料|Labで読めるもの|扱わないもの|
|---|---|---|
|図3、付録C.1|run.py の allocate(counterexample) と、入荷のたびに置いた先を示す図|2拠点の解析解のみ。一般の拠点数の解法は扱わない|
|式(6)–(7)、命題2|allocate(state)。拠点ごとに分けられる区分線形残差と、配置後の在庫にかかる二次の項|正負の重みで複数拠点を密に結び付ける場合や、モデルの学習|
|式(5)|allocate(action)。配置後ではなく、その回に置く量に項を加えたLab独自の比較|論文の学習済み比較方策の再現|
|式(9)–(10)、定理1|手法の説明と、H⁻¹1=(2,−1) の負成分が示す反例|定理の新しい証明や、一般条件での数値検証|
|表1・図4・式(11)|paper_evidence と費用棒図。長期費用と、環境を固定して分割回数を変えたときのTVを別に示す|値は著者報告の転記。学習条件が違う二つの実験を混ぜない|
|付録B.2–B.3|State-proxの手法紹介|配置を求める順方向の計算と、学習に使う逆方向の計算の実装|

原論文：[2609.23242v1](https://arxiv.org/abs/2609.23242v1)。提供PDFで公式コードへのURLを確認できなかった。公式実装は実行せず、図は数式と報告値から作成した。

他のLabとの関係はLabの解釈。[Diff Projection](diff-projection-feasible-multi-echelon-inventory.html)は複数拠点で共有する制約の下で生産・在庫の行動を決める。[DeepStock](deepstock-policy-regularized-inventory-drl.html)と[ORPR](orpr-or-guided-pretrain-reinforce-inventory.html)は補充量を決める。どの研究も同じ条件で性能比較したわけではない。

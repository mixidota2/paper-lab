ApolloPFNは **Temporal-Feature Factorized Transformer**。時間N × 特徴F × 埋め込みDのテンソルを扱い、特徴方向のattentionと時間方向のattentionを順に行う。時間方向にはRoPEと絶対位置のsin/cos表現を加える。将来時点同士も参照できるが、将来の目的変数はマスクする。

事前学習の課題は **Single Root Node Growing Network（SRNGN）** で作る。sin/cosの時間信号を根に置き、ランダムなMLPと雑音を持つ構造的因果モデルに伝播させ、途中のノードから説明変数と目的変数を選ぶ。ここでいう因果グラフは合成データの生成装置であり、実店舗の因果関係を推定したものではない。

対象系列を使うときは重みを更新せず、過去の値と将来に利用可能な外生変数から分布を出す。小実験は販促予定のずれだけを扱い、PFNの事前学習もattentionも実装していない。

[一次資料：方法と実験条件](https://arxiv.org/html/2603.15802)

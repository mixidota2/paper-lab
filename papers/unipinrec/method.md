UniPinRecは **PinRecのcausal decoder-only Transformer** を候補生成と順位付けで共有する。商品入力はOmnisageやCLIP系の事前学習表現、検索語は検索埋め込みを使い、MLPで射影する。

Masked Action Modeling（MAM）は商品表現と行動表現を特徴方向に結合する。候補の行動は常に[MASK]で、未観測と「行動なし」を区別する。履歴には次商品予測のsampled softmax、順位付けにはクリック・保存・非表示などの行動別BCEを使い、同時に学習する。

配信時は履歴のKey/Valueを段間で共有する。候補は履歴を参照できるが、他候補は参照しない。このattention構造が、候補集合を変えても履歴を再利用できる理由になる。

[一次資料：方法と実験条件](https://arxiv.org/html/2606.00422)

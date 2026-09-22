### adapterは学習recipeではない

必須はsid_assignments(item_id, sid_0, …, sid_L)。method/datasetラベルとprovenanceを添え、metadata、interaction、refresh pair、generator traceを同じitem keyへjoinする。key重複、missing code、深さ不一致、item countの不一致を先に拒否する。検査前の壊れたtableを診断値へ平均して隠さない。

### D1–D5が測る対象

D1はlevelごとの利用code数、entropy、不均衡、prefix数。D2はfull SIDを共有するbucketに入ったitemの割合で、重複したcode値の個数とは違う。D3はtrain interactionから作ったco-occurrence top-k近傍のうち、同prefixを保つ割合。edge重み付きとitem平均を分ける。metadata purityは補助的な文脈であり、行動的一致の代用ではない。

D4はpopularityでhead/mid/tailを分け、unique SID配分やprefix構造を点検する。D5は深さ・active prefix・fan-out等の構造費用を記録する。生成model・GPU・beamを測らずに、D5からserving latencyを主張しない。

### 一意住所と近傍を、同じitem集合で比べる

主比較はGRID/RQ-KMeans-styleとReSID/GAOQの23,742 Musical item。RQ-minは小さい参照adapter、category-prefixやhash-collideは診断を動かすcontrolである。LETTERとLC-Recはreleased item-indexを読み込めることの確認で、同じitem集合の性能順位へ加えない。

D6はpaired refresh mappingのchurnを計算する実装済み拡張。D7はgenerator traceが渡されたときのinterface hookで、本文の実証対象ではない。[VARG](varg-tmall-value-generative-retrieval.html)のように日次住所固定を採る場合、D6で旧item churnと新itemのalias増加を別に追うという接続が考えられる。これはLab側の運用解釈である。

[SIDScope](sidscope-diagnostics.html)もmapping・alias・prefix・handoffを扱うため、診断名の数を新規性と数えない。SIDInspectorを選ぶ具体的な理由は、手元のexportを小さい契約へ変換してD1–D5へ通せるかで判断したい。

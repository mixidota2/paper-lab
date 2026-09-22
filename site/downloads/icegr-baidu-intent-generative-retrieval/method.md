### 量子化前に検索で結ばれる商品を集める

8BのEC適応embedding modelでquery–product InfoNCEを学び、co-click graphを作る。edgeは同じqueryからのclick数の幾何平均を合計する。対称正規化した隣接行列で3回伝播し、各回0.2の元embeddingを混ぜる。

さらに各商品の歴史query embeddingをclick頻度で加重平均する。query数に基づくη=min(1,log(|Qᵢ|+1)/log(51))をかけてgraph表現へ加算し、L2正規化する。fusion λ=1、最終256次元。3層・各1,024 codeのRQ-KMeansでSIDを作る。VARGの第3 tokenの価値順とは異なり、3層とも残差量子化である。

### 商品の暗記課題をqueryの教師へ変換する

SQE-SFTはcatalogからSPU、brand、category、series、model、attributeを抽出する。商品名・category・variantを指定するqueryと、属性条件付きqueryを作り、正規化・dedup・validity filteringを行う。Stage 1 synthetic→SID、Stage 2 real→SIDの共通目的で学ぶ。低露出商品のquery教師を増やすことが狙いであり、実際にそのqueryでclickされた証拠を増やす操作ではない。

### RCPOは関連性を守りながら比較の強さを変える

0.6B relevance modelのSRSと、click・purchase・GMVからcategory平均へ平滑化したSBPを用いる。SRAは関連性で選好方向を決め、BPRは関連性の近い候補間でbusiness順を決める。SRS/SBPを[0,1]へ揃えた等重み平均rからΔr=r⁺−r⁻を計算する。

βeffは大きい正marginほど小さくなる。既にoffline根拠が明白なpairへの重複した更新を弱め、僅差のpairを強くする設計である。ただしβはsigmoid内の係数なので、実際のgradientの大きさは現在のpolicy比にも依存する。正解SIDへのlength-normalized SFT項も残す。

backboneはoffline比較・onlineとも0.5B。1.5/3/7Bでも検討するが、本文で確認できるのはサイズであり、Qwenなどの固有model名を補わない。

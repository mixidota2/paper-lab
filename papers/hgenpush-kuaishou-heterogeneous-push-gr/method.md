### 作者の意味空間は行動から整える

入力はlong/short feed、push click、push sendとstatic feature。共有backboneはcausal self-attention、RMSNorm、SwiGLUを持つdecoder-only。videoとauthorの[cls]位置からinterestを取り出す。主設定は16層、hidden 512、codebook size 8,192。videoは3 code、authorは2 codeを使う。

author特徴とuser interestをInfoNCEで整合させ、author側をRQ-Kmeansで離散化する。SimVQでcodebook collapseを抑える。mixed SIDは(author₁, author₂, video₁)で、作者とその作者のどの動画群を選ぶかを結び付ける。

### Chained-MTPはSIDの依存を捨てない

各level kは同じuser anchorと、j<kのtoken embeddingの和を入力にする。trainingでは教師tokenを使えるためFFNを並行計算できる。inferenceにはbeamとprefixへの依存が残る。「重い自己回帰decoderを繰り返さない」と「独立予測」は違う。

### 消費報酬をsequence単位で重み付けする

UCPAのrewardはvalid play / profile遷移 / comment滞在で+2、like / follow / share / commentで+1、short play −2、dislike −5、report −10を一致条件ごとに加算する。session内の動画を最大50件のgroupとして標準化する。GSISPOはsequenceの確率比の幾何平均をclipし、stop-gradientの重みとしてlog-probabilityへ掛ける。SFT lossも残すため追加KLを使わないと記述する。std=0のgroup処理など、実装に必要だが本文だけでは確定できない点は補って断定しない。

<figure class="teaching"><h3>二つのSID経路が、同じrankerへ入る</h3><div class="b21-serving"><section><h4>Video branch</h4><p>multimodal video → 3-level SID</p><p><strong>[video₁, video₂, video₃]</strong></p><p>video候補へ展開</p></section><section><h4>Author branch</h4><p>行動整合 → 2-level author SID</p><p><strong>[author₁, author₂, video₁]</strong></p><p>作者とvideo群で候補を限定</p></section></div><p>両branch → pre-rankを迂回 → <strong>既存ranking model</strong> → push候補</p><figcaption><a href="https://arxiv.org/pdf/2607.03362v1">§3.2–3.4 / Fig. 1</a>を再構成。候補生成の出力型と下流の責任を示す。</figcaption></figure>

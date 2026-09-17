### 4段のSIDをrankingへ入力する

§3.1・式1–2。multimodal表現をRQ-VAEで4段、各256 codeへ量子化する。SID embeddingを連結してranking学習で調整する。RQ-VAEは10 epochs、batch4096、codebook embedding64。ranking側SID embeddingは32、AdamW、3層ReLU MLPでCTRとCTCVRを扱う（§4.1.3）。

### GFSAはattention分布を混ぜる

§3.2・Algorithm 1、式4–8。商品のID embedding e_itemと統計特徴F_statを連結し、`w=σ(MLP([e_item ⊕ F_stat]))`。統計特徴には掲載期間、直近1週間の露出・クリックが入る。

意味内と行動内で別々にattentionを作る：`S_sid=softmax(Q_sid K_sidᵀ/√d)`、`S_item=softmax(Q_item K_itemᵀ/√d)`。

その後に `S_fused=w S_sid+(1−w)S_item` とし、`h_sid=S_fused H_sid`、`h_item=S_fused H_item` を連結してranking層へ渡す。他モダリティのKeyに直接Queryを当てるcross-attentionでも、最終embeddingを単純平均するだけでもない。

### GRCAは同じgateで整列を調整する

§3.3・式9–11。同じ商品のSID/ID表現をpositive、batch内の別商品をnegativeにして `ℓ_cl(i)=−log[exp(sim(e_sid_i,e_item_i)/τ)/Σ_j exp(sim(e_sid_i,e_item_j)/τ)]` を計算する。

`L_total=L_rank+λ |B|⁻¹ Σ_i w_i ℓ_cl(i)`、実験λ=0.1。wが大きい商品では意味の寄与と対照整列がともに強くなる。wは学習結果なので、掲載20日で機械的に切り替える関数ではない。20日は評価cohortの境界だ。

出典：[2603.22916v2](https://arxiv.org/pdf/2603.22916v2)。上記で「Lab」とした式・条件は説明用の補助である。


<figure class="teaching batch17"><h3>gateを動かして、履歴の重みと整列強度を見る</h3><div data-b17="gate"><label>意味側の重みw（人工入力）<input data-control type="range" min="0" max="4" value="2" step="1"></label><p data-output aria-live="polite">w=0.5：両分布を等しく混ぜる。日数から学習したgateではない。</p><script type="application/json" data-values>[{"weight": 0, "sid_attention": [0.7869860421615985, 0.10650697891920076, 0.10650697891920076], "item_attention": [0.10650697891920076, 0.10650697891920076, 0.7869860421615985], "shared_attention": [0.10650697891920076, 0.10650697891920076, 0.7869860421615985], "sid_pooled": [0.15976046837880115, 0.8402395316211989], "item_pooled": [0.10650697891920077, 0.8934930210807993], "weighted_alignment_loss": 0.0}, {"weight": 0.25, "sid_attention": [0.7869860421615985, 0.10650697891920076, 0.10650697891920076], "item_attention": [0.10650697891920076, 0.10650697891920076, 0.7869860421615985], "shared_attention": [0.2766267447298002, 0.10650697891920076, 0.6168662763509991], "sid_pooled": [0.3298802341894006, 0.6701197658105995], "item_pooled": [0.24260279156768033, 0.7573972084323197], "weighted_alignment_loss": 0.0309682395923419}, {"weight": 0.5, "sid_attention": [0.7869860421615985, 0.10650697891920076, 0.10650697891920076], "item_attention": [0.10650697891920076, 0.10650697891920076, 0.7869860421615985], "shared_attention": [0.44674651054039966, 0.10650697891920076, 0.44674651054039966], "sid_pooled": [0.5, 0.5], "item_pooled": [0.3786986042161599, 0.6213013957838402], "weighted_alignment_loss": 0.0619364791846838}, {"weight": 0.75, "sid_attention": [0.7869860421615985, 0.10650697891920076, 0.10650697891920076], "item_attention": [0.10650697891920076, 0.10650697891920076, 0.7869860421615985], "shared_attention": [0.6168662763509991, 0.10650697891920076, 0.2766267447298002], "sid_pooled": [0.6701197658105995, 0.3298802341894006], "item_pooled": [0.5147944168646394, 0.48520558313536066], "weighted_alignment_loss": 0.09290471877702569}, {"weight": 1, "sid_attention": [0.7869860421615985, 0.10650697891920076, 0.10650697891920076], "item_attention": [0.10650697891920076, 0.10650697891920076, 0.7869860421615985], "shared_attention": [0.7869860421615985, 0.10650697891920076, 0.10650697891920076], "sid_pooled": [0.8402395316211989, 0.15976046837880115], "item_pooled": [0.650890229513119, 0.3491097704868811], "weighted_alignment_loss": 0.1238729583693676}]</script></div><p>S_sid → <strong>w</strong> ／ S_item → <strong>1−w</strong> → S_fused → 両方の履歴をpool → ranking</p><p>同じw → w × InfoNCE → ranking lossに加える</p><figcaption>§3.2–3.3、式4–11の人工数値例。sliderは成熟日数や実測AUCを表さない。</figcaption></figure>

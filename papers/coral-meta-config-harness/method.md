### 非定常な予算付き最適化として表す

§3・式1–2。control unit iの設定s_iをまとめ、時点tの目的J_tと費用c_tに対し、`s*_t=argmax_s J_t(s), subject to c_t(s)≤B`。狙いは固定した一つの最適点への収束より、移動する最適点に対する累積損失 `Σ_t[J_t(s*_t)−J_t(s_t)]` を減らすこと。これを最小化する保証やregret boundを証明した論文ではない。

LLMは集約観測o_tと記憶M_tから提案を作る。数値optimizerが許容集合への最も近い設定を返す。提案が既に予算内なら変更しない（§4.2）。距離関数やoptimizerの詳細は開示されないため、Labでは明示したEuclidean projectionに限定する。

### 固定順序で回し、三種類の記憶を持つ

§4.1–4.3。observation storeは運用統計、assessment storeは言語化した評価、decision storeは適用設定と帰属した結果を保持する。analysis→retrieval→attribution→提案→optimizer→applyを固定順で実行し、制御フローをLLMに任せない。実装の周期k=3日、記憶m=3 cyclesは合理的な初期値として選び、最適化した値ではない。

Appendix A・図2のpromptは各unitのbounded adjustment、rationale、confidenceと全体assessmentをJSONで返す。retrievalの例ではsourceごとの連続multiplier、servingの例ではuser segmentごとの離散menuから選ぶ。実行は自律でも人の監督が残る。

### 配信費用とLLM費用を分ける

§6・式3は `Cost=(T/k)·C·(τ_in p_in+τ_out p_out)`。呼出し回数Cはdecision group数に依存し、利用者のrequest数には比例しない。表2はretrievalで約10 calls/cycle、入力約1500・出力約2500 tokens/call、servingで約8 calls、入力約2000・出力約2500。token usageはlogされておらず、これらは推定。数十USDという費用も実測請求額ではない。

出典：[2609.02730v1](https://arxiv.org/pdf/2609.02730v1)。上記で「Lab」とした式・条件は説明用の補助である。


<figure class="teaching batch17"><h3>提案と予算保証の責任を分ける</h3><div class="b17-cards"><div><strong>観測・記憶</strong><p>source / segmentの統計、前回設定、帰属結果。m=3 cycles。</p></div><div><strong>LLMの提案</strong><p>連続multiplierまたは離散menu。理由とconfidenceを添える。</p></div><div><strong>数値optimizer</strong><p>予算内ならそのまま。超過なら最も近い実行可能な設定へ。</p></div><div><strong>配信と測定</strong><p>k=3日周期。A/Bまたは観測結果を記憶へ戻す。人の監督は残る。</p></div></div><figcaption>§3–4・図1。数値optimizerがengagementの改善まで保証する図ではない。</figcaption></figure>

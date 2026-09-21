### 国ごとに学習し、領域をまたいで履歴を使う
V1/V2のclassifierは4層・4 head・幅128、FFN幅160のencoder-only Transformer。BERT4Rec型の双方向attentionを使い、直近購入の店舗IDとproduct lineだけをmaskする。request時刻とH3位置は既知なので残す。targetの正解product lineを入力すると漏洩になる。V3は4層のまま6 head・幅192・FFN幅384へ拡大する。

店舗、product line、週、曜日、時刻、H3 cellの埋め込みと、log変換した経過時間を使う。全店舗のlogitを1回のforwardで出し、配達可能な候補のlogitだけを取り出す。CatBoostはこの1スカラーにrating、CVR、距離、配送料、click履歴、平均basketなどを加える。最終scoreは g(i)=CatBoost(hᵢ,xᵢ)。Transformerだけで最終順位を作る設計ではない。

転移するのは同じ国の飲食店と小売の履歴である。国ごとに語彙とモデルを学習し、国間転移の実験はしていない。V3でも構造の異なる特徴を扱うため、飲食店と小売のCatBoostは別に持つ。「4 rankerを一つへ統合」は配信システム全体の記述で、木モデルが一個になったという意味ではない。

### trialの重みと漏洩防止を明示する
classifierのlabel smoothingはε=0.2。正解の質量を1−ε、各クラスへε/|domain|を配り、w_new > w_cs > w_recでCEを重み付けする。V1のrankerはPairLogit、V2/V3はYetiRankPairwiseのNDCG mode。購入labelはtrial/reorderで同じとし、trialの優先度はsession重みへ置く。clickは購入より弱い段階labelにする。

rankerは直近30日のうち28日を学習、次の1日をvalidation、最後の1日をtestに使う。classifierの学習を2日前で切り、ranker評価日の正解がlogitへ漏れないようにする。購入なしsessionを除外しているため、このオフライン評価だけで全sessionのCVRは説明できない。

<figure class="teaching batch21"><h3>trialを押すほど、reorderを失う領域がある</h3><div class="b21-frontier"><div><strong>重み比 1</strong><label>trial MRR <meter min="0" max="1" value="0.5"></meter> 0.5</label><label>reorder MRR <meter min="0" max="1" value="1.0"></meter> 1.0</label></div><div><strong>重み比 2</strong><label>trial MRR <meter min="0" max="1" value="0.73361"></meter> 0.73361</label><label>reorder MRR <meter min="0" max="1" value="0.75899"></meter> 0.75899</label></div><div><strong>重み比 3</strong><label>trial MRR <meter min="0" max="1" value="1.0"></meter> 1.0</label><label>reorder MRR <meter min="0" max="1" value="0.5"></meter> 0.5</label></div><div><strong>重み比 5</strong><label>trial MRR <meter min="0" max="1" value="1.0"></meter> 1.0</label><label>reorder MRR <meter min="0" max="1" value="0.5"></meter> 0.5</label></div></div><figcaption>run.pyの合成400 test sessions。原典Appendix Aの150 retrainの数値を模写したものではない。</figcaption></figure>

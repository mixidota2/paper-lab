### 構成は属性2段＋SID3段

§4.1.1の設定では、SIDは3層、各codebook K=4000、capacity許容τ=1.05。CoAはカテゴリL2→L3を先に生成する。本文のcategory/seller/brandは一般的な属性候補で、実験の全使用属性を意味しない。

§3.5のbackboneはdecoder-onlyに履歴へのcross-attentionを加えた構成。d_model=256、行動履歴200、multimodal SID系列100、cross-attention 3層×8 heads、SwiGLUのMMoE-FFN 4 experts。各stepのRank HeadにはSENetとMaskNetを使い、prefix embedding、Content Summary、ユーザー集約表現を渡す。履歴がKey/Value、task・属性・SID列がQueryになる。

### 露出capacityとCoAの式

式1–2は `V_k = Σ_{i:z_i=k} w_i`、`C_cap = Σ_i w_i / K` とし、再構成誤差 `Σ_i ||x_i−μ_z_i||²` を `V_k ≤ τ C_cap` の下で最小化する。Algorithm 1は最近傍割当の後、過負荷clusterから余裕のあるclusterへ移す近似解法。

式5のCoAは `p(a,s|u)=Π_j p(a_j|a_<j,u) Π_l p(s_l|s_<l,a,u)`。式6のentropy差は `H(S_l|S_<l,U)−H(S_l|S_<l,A,U)=I(S_l;A|S_<l,U)≥0`。これは分布上の平均の恒等式で、すべての生成prefixで精度が上がる保証ではない。

### Bayes同値性で落ちている条件

【Labの検討】式3は `p(y|f,u) ∝ p(f|y,u)p(y|u)` と書くが、fを変えて順位を比較するなら `p(y|f,u)=p(f|y,u)p(y|u)/p(f|u)` が一般形である。p(f|u)が一定、またはその補正を行うという条件が要る。人工例では人気商品Aの事前確率0.9・engagement 0.2、希少商品Bは0.1・0.8とする。p(f|y=1,u)だけで並べるとAが上位になり、判別scoreの順位と逆転する。CoAの実験上の有効性を否定する反例ではなく、同値性の適用範囲を限定する反例だ。

### CDCと目的関数

Task-Conditioned BOSは面と行動目的を開始tokenに埋め込む。Content Summary（式7）はprefix属性・SIDの組を複数hashで共有embeddingへ写し、各Rank Headへ渡す。実験は3 hash、hash次元64。単なる長いprompt化ではなく、組合せを明示する補助特徴である。

RFTはGMVなどの予測価値をbatch内で正規化・clipしてNTPを重み付けする（式21–24）。DPOは同一request内のpurchase > click > exposureの対を比較し、referenceに対するlog確率比の差へlog-sigmoidを適用する（式25–27）。両損失の重みは20:3、DPO β=0.1。式28では最終SID層以外をstop-gradientにし、prefixの予測を保つ。

出典：[2604.12234v4](https://arxiv.org/pdf/2604.12234v4)。上記で「Lab」とした式・条件は説明用の補助である。


<figure class="teaching batch17"><h3>どこで属性と履歴が出会うか</h3><div class="b17-cards"><div><strong>履歴 → Key / Value</strong><p>200行動と100のmultimodal SID系列。ユーザーの情報を保持する。</p></div><div><strong>BOS → L2 → L3 → s₀ → s₁ → s₂</strong><p>taskで開始し、カテゴリを先に予測。各SIDは属性とprefixに条件付く。</p></div><div><strong>各stepのRank Head</strong><p>cross-attention出力 + prefix + hash Content Summary + ユーザー集約 → SENet / MaskNet。</p></div></div><figcaption>§3.4–3.5・図1、§4.1.1。seller/brandは一般例で、ここでは実験設定のL2→L3を示す。</figcaption></figure>

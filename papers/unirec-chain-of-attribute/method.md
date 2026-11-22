### 先に予測する属性とSIDの構成

§4.1.1の設定ではSIDは3層あり、各codebookの大きさはK=4000、露出上限の許容係数はτ=1.05。CoAはカテゴリのL2を生成し、続けてL3を生成してからSIDへ進む。本文のcategory/seller/brandは属性の候補を挙げたもので、実験でそのすべてを使ったという意味ではない。

§3.5のモデルは、履歴を参照するcross-attentionをdecoder-onlyの構成に加える。d_model=256とし、行動履歴200件、multimodal SID系列100件を入力に使う。cross-attentionは3層×8 headsで、SwiGLUを使うMMoE-FFNには4 expertsがある。履歴をKey/Valueに、task・属性・SIDの列をQueryに使う。各stepのRank Headでは、prefix embedding、Content Summary、ユーザー履歴を集約した表現をSENetとMaskNetに渡す。

### 露出上限とCoAの式

式1–2ではcluster kに割り当てた商品の露出の合計を `V_k = Σ_{i:z_i=k} w_i`、cluster当たりの基準を `C_cap = Σ_i w_i / K` とする。再構成誤差 `Σ_i ||x_i−μ_z_i||²` が小さくなるように、割当を `V_k ≤ τ C_cap` の範囲で選ぶ。Algorithm 1は、まず商品を最も近いclusterに割り当て、上限を超えたclusterから余裕があるclusterへ商品を移す近似解法だ。

式5のCoAは `p(a,s|u)=Π_j p(a_j|a_<j,u) Π_l p(s_l|s_<l,a,u)`。属性列aを順に予測し、属性aを条件に加えてSID列sを順に予測する。式6では、属性Aを条件に加えたときに減るentropyが `H(S_l|S_<l,U)−H(S_l|S_<l,A,U)=I(S_l;A|S_<l,U)≥0` となる。分布上で平均したときの恒等式であり、すべての生成prefixで精度が上がる保証ではない。

### 生成と判別の順位が一致する条件

【Labの検討】式3は `p(y|f,u) ∝ p(f|y,u)p(y|u)` と書く。商品fを変えて順位を比べる場合、一般形の `p(y|f,u)=p(f|y,u)p(y|u)/p(f|u)` では分母も商品によって変わり得る。式3の比例関係だけを根拠に、生成と判別で同じ順位になるとは言えない。p(f|u)が商品間で一定なら分母を省けるが、一定でなければ分母の違いも含めて比べる。

人工例では、人気商品Aの事前確率を0.9、engagementを0.2、希少商品Bの事前確率を0.1、engagementを0.8とする。p(f|y=1,u)だけで並べるとAが上位になるが、判別scoreではBが上位になる。これは生成と判別の同値性に条件が要ることを示す例で、CoAの実験上の有効性を否定するものではない。

### CDCと学習の目的関数

Task-Conditioned BOSは推薦を出す面と行動の目的を開始tokenに埋め込む。Content Summary（式7）は属性とSIDのprefixの組を複数のhashで共有embeddingに写し、各Rank Headへ渡す。実験では3 hash、hash次元64を使う。promptを長くするだけではなく、組み合わせを明示する補助特徴を渡している。

RFTはGMVなどの予測値をbatchの中で正規化・clipし、その値でNTPを重み付けする（式21–24）。DPOは同じrequest内のpurchase > click > exposureの順で対を比較する。各項目についてreferenceに対するlog確率比を求め、対の差にlog-sigmoidを適用する（式25–27）。両損失の重みは20:3、DPO β=0.1。式28では最終SID層以外でstop-gradientを適用し、prefixの予測を保つ。

出典：[2604.12234v4](https://arxiv.org/pdf/2604.12234v4)。「Lab」と記した式や条件は説明用の補助である。

<figure class="teaching batch17"><h3>モデルに渡す履歴と生成した属性</h3><div class="b17-cards"><div><strong>履歴 → Key / Value</strong><p>200件の行動と100件のmultimodal SID系列からユーザーの情報を渡す。</p></div><div><strong>BOS → L2 → L3 → s₀ → s₁ → s₂</strong><p>taskを示す開始tokenの後にカテゴリを予測する。各SIDの予測には属性とそれまでのprefixを使う。</p></div><div><strong>各stepのRank Head</strong><p>cross-attentionの出力、prefix、hashで写したContent Summary、ユーザー履歴を集約した表現をSENet / MaskNetに渡す。</p></div></div><figcaption>§3.4–3.5・図1、§4.1.1。seller/brandは一般例で、図は実験設定のL2→L3を示す。</figcaption></figure>

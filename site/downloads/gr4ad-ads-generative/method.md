### UA-SIDは動画だけでなく商品と広告主を読む
広告の表現UAEは、動画の視覚・ASR・OCRなど、商品の価格・title、advertiserの地域や属性を統合する。原典Table 2はbackboneをQwen3-VL-7Bと表記する。本Labではこのモデル名を原文に従って記し、別の公開モデル名へ補正しない。instruction tuningに加え、同時出現するVideo/Product/Advertiserの組を正例、batch内の他例を負例とするInfoNCEで表現を学ぶ（§3.1、式1）。

残差量子化は各段で近い中心を選び、残差を次段へ渡す。MRは初期のcodebookを大きくし、意味の大きな違いを先に分ける。各段はbalanced k-meansで利用の偏りを抑える。MGはitem/account IDやconversion typeなどをhashし、最後の数値層へ置く。同じ意味の広告を業務上区別する役割を持つ（Figure 2）。hashなので衝突ゼロの保証はない。

### VSLは価値を加味した模倣、RSPOはlistの相対順位を学ぶ
VSLはSIDの次token予測に、等頻度bucketへ離散化したeCPM tokenの予測を加える。このtokenはSIDの後に置かれ、生成広告の並べ替えに使える。ユーザーの長期広告価値と行動の深さの積をsample weightにする。

`L_NTP = −Σ_t log p(s_t | s_<t, X) − λ_e log p(v_bucket | y, X)`

`L_VSL = E[w_user w_behavior (L_NTP + λ_mtp L_MTP)]`

MTP補助損失は、後述の前tokenを注入しない経路にも予測力を持たせる。SID出力を当てるだけで前半層を使わなくなるのを避ける狙いがある。

RSPOは報酬v_i（eCPM）の低い候補集合 `E_i = {j : v_j < v_i}` に対して、次の損失を使う。式16を読みやすく置き換えると、

`a_ij = β[log pθ(y_j|X) − C_ij log p_ref(y_j|X) − log pθ(y_i|X) + C_ij log p_ref(y_i|X)]`

`L_RSPO = E_i log₂(1 + Σ_(j∈E_i) M_ij exp(a_ij))`

ここで `M_ij = (1/D_|i−j| − 1/D_(|i−j|+1)) |G_i−G_j|`、`D_i=log₂(1+i)`、`G_i=(2^v_i−1)/Z`、Zはideal DCGである。RSPOでは、例えば報酬順位1位の広告が3位の広告より低いscoreになると損失が増える。順位間隔と価値差に応じて重みが変わる。単純なchosen/rejectedの二者比較よりlist全体を扱う。

C_ijは参照分布が利用可能で信頼できるとき1、それ以外は0。原典式18は対象集合内の平均log確率比が閾値δ未満かで判定する。別pipeline由来のsampleや古い参照分布を扱う工夫である。Appendix A.1のNDCGcostの上界という議論は、このscoreと重みの定義に関するもので、真の収益改善の保証ではない。

### UVRは順位のずれで学習の配分を変える
モデル確率の順位r_pと報酬順位r_vから `A(i)=|r_p(i)−r_v(i)|/(n−1)` を計算する。ずれが大きいとVSL、小さいとRLを強める。

`w_VSL(i)=w₀ exp[A(i) log(1+v_i)]`

`w_RL(i)=w₀ Z_max (1−A(i))`

`L=E_i[w_VSL(i)L_VSL(i)+w_RL(i)L_RSPO(i)]`

著者はこれを安定した興味分布と価値探索の調整と説明する（式19–22）。research_botの批評として、順位の一致だけではユーザー満足も報酬の校正も分からない。報酬モデルが同じ誤りを繰り返せばAが小さくても危うい。

### LazyARは前tokenの注入を後ろへ遅らせる
通常のARは前tokenのembeddingを最初の層へ入れ、各SID段で全decoderを計算する。LazyARではposition embeddingから先頭K層の状態mを先に計算し、`Fuse(m,s)=W_f[m ⊙ (W_g s); s]` で前tokenを注入する。その後L−K層を逐次実行する（式5–11）。層はOneRec-V2に従うcross-attention、self-attention、FFNとpre-layer normで構成する。

実験構成はL=9、K=6。前半6層は各生成位置について先に計算でき、beam間で共有する。後半3層が候補別の逐次処理を担う。第1SIDの生成は全層を通す。短いSIDと大きなbeamに適した節約であり、長文の通常LLM decodingへそのまま一般化しない。

### DBSは階層ごとの幅と時間帯ごとの幅を変える
Dynamic Beam Widthは[512,512,512]を[128,256,512]へ変え、最終候補数を保って前半を縮める。TABSは混雑時のbeamを維持し、閑散時に60%増やして余剰計算を探索へ回す。`B_t=B_base f(Q_t,C_avail)` の関数形は詳述されないため、完全なcontrollerは再実装できない（§4.2）。

reward systemでは実露出から学んだ価値モデルで、より広いbeamと探索により得た候補を採点する。そのログとVSLログで継続学習し、servingへパラメータを同期する。新規広告はUA-SID↔item indexへ追加する。[TAGR](tagr-live-sid.html)が扱う時間変化に応じたSID更新は別の軸であり、GR4ADのhashによる識別と補完的に検討できる。

[一次資料：arXiv v3](https://arxiv.org/pdf/2602.22732v3)

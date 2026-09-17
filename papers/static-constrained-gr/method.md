### 許可集合Cを先に定める

§4.1。SID長L、語彙V、許可された系列集合Cに対し、`F_t(prefix,v)=1{∃c∈C: prefix+v は c のprefix}` とする。無効な次tokenのlog確率を−∞へ落とす。SID一般のvalidityと、鮮度・在庫・カテゴリなどで限定したCへの所属は別の判定だ。

Algorithm 1はまずLogSoftmaxを計算し、その後にmaskを適用する。制約後に再正規化するとprefix間のbeam scoreが変わるため、この順序も対応表に残す。最小実験はscoreの再正規化を扱わず、許可経路そのものを全列挙する。

### trieをCSRの三配列へ写す

§4.2。各prefixへstate番号sを割り当て、`T[s,v]=next_state` を疎行列として持つ。`indptr[s]:indptr[s+1]` がそのstateの子の範囲、列番号がtoken、値が次stateになる。論文の0はsinkを表す。Labの簡略実装はroot=0とし、無効遷移をFalseで返すので、この番号規約だけは異なる。

最初のd層はdense maskとstate table、残りをCSRにする。実験はd=2、V=2048なので最初のtableは2048²。VNTKは層ごとの最大分岐数で固定長sliceを読み、paddingの有効範囲をmaskする。beamを選び直した後は対応するstateも同じ順でgatherする。Appendix Aではtokenと遷移先をstackしたCSRによるread削減を説明している。

### 遅延測定の条件

§5.1–2。Gemini系、PLUMに近いdense 3Bモデル、SID長8、beam70、batch2/chip、TPU v6e。全候補は約100M–1B、制約集合は直近7日の高品質動画約20M。表1の時間は各decode stepの制約追加処理であり、モデルforward全体の時間ではない。

CPU trie baselineにはTPU↔CPU同期を含む。PPV Exactは全2048 logitsを検査し、Approximateはtop50だけを検査する。後者やfalse positiveを許すhash bitmapとは厳密性が一致しない。

出典：[2602.22647v2](https://arxiv.org/pdf/2602.22647v2)。上記で「Lab」とした式・条件は説明用の補助である。


<figure class="teaching batch17"><h3>同じSIDでも、有効集合と業務集合は違う</h3><div class="b17-cards"><div><strong>全valid SID</strong><p>000 / 001 / 010 / 100 / 111</p></div><div><strong>fresh集合 C</strong><p>001 / 111 の2件だけ。古いvalid SIDは除外する。</p></div><div><strong>prefix 0 の次token</strong><p>0だけが可能。01はvalid catalogにあってもfreshにはない。</p></div></div><figcaption>人工2値・3段ID。§4の集合制約を教えるための例で、YouTubeの実SIDではない。</figcaption></figure>

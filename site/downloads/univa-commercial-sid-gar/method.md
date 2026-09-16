### Commercial SIDは末尾を「属性の組×入札bin」に替える

テキスト・画像・動画由来の意味をRQ-KMeans+で量子化し、上位2段を残す。最終段は最適化目標o、ROI目標r、業種cを圧縮した組k=(o′,r′,c′)と、その組の中でのbid分位点から作る。全体でbidだけを切る方式ではない。v2付録F.1では属性の区分数は25・8・10、3件未満の組はfallbackへ統合。各組に3〜25binを配り、語彙予算2048の下でtoken entropyを最大化する。付録CのClassify-then-Bin＋等頻度分割はH=7.487、実語彙1939だった。

同じCSIDを複数の広告が共有する。配信時には適格な広告だけを葉に残し、その葉の最大bid広告を選ぶ。CSIDを一意の商品IDや、入札の絶対値をそのまま表す数値と見なさない。

### 生成ヘッドとaction-valueヘッドが同じdecoderを使う

HSTU encoderはUser・Organic・Environment・Item tokenを受け取る。decoderはencoderへのcross-attention、causal self-attention、sparse MoEを使い、MoRの中間層を反復共有する。Fullは埋め込み256、実効6層、64 routed expertsのTop-16、80M decoder parameters。encoderを含むモデル総数ではない。

生成ヘッドは次tokenのlogit o_gen、価値ヘッドはprefixでtoken aを選んだ後の商用return qφを出す。GARはo_gen+α_l qφを加算する。α_lはvalidationで選び、オンラインでは固定する。値の単位・較正が違うため、単にbidをlogitへ足す手法ではない。[v2 式15–16](https://arxiv.org/pdf/2605.05803v2)

### eCPMを終端報酬にし、価値ヘッドを配信にも残す

SLの次token交差エントロピーとRLのbatchを交互に使う。RLでは旧方策のbeamと価値誘導MCTSで軌跡を集め、production rankingのpCTR・pCVR部品を固定したoffline simulatorで終端eCPMを計算する。request内で平均を引き標準偏差で割る。PPOは生成方策を更新し、価値ヘッドはreturnへ回帰する。baseline V_oldは有効token上の旧方策確率でq_oldを平均する。MCTSとsimulatorはオンラインでは動かない。

maskをGAR logitへ加えてからsoftmaxを取り、その対数をprefixに沿って累積する。日次で約500万creativeのライブラリを作り、targeting、広告の配信状態、creative制約でrequest別trieを得る。独立したオンラインrerankerを呼ばないという主張は、この生成経路内の設計についてのものだ。[v2 §3.3–3.4、付録B/F](https://arxiv.org/pdf/2605.05803v2)

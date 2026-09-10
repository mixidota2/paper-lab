### LSIDはユーザーごとのIDにしない
scene encoderは配信者の過去の販売スタイル、現在の映像、場面特徴を読む。product encoderは商品テキスト、属性、注文状態などを読む。user encoderは長期興味とprofileを扱う。三つともReLUつきMLPで共有空間へ写す（§2.2）。

`L_align = L_U2S + L_U2P + L_S2P`

入室でuser–scene、カートクリックでuser–product、共起でscene–productを対照学習する。割当には次の融合表現を使う。

`z_live(t) = normalize(α s(t) + β p(t))`

`y_a(t) = RQ-KMeans(z_live(t)) = (s₁,…,s_D)`

協調情報は表現学習に入るが、同じ時刻の広告はリクエストによらず共通のIDを持つ。最終階層には配信者を考慮したhash bucketを使う。現行広告は毎分再符号化し、正規の割当をstorageへ書き、数秒以内に双方向LSID–LiveID索引へ伝える（§3.2）。固定するのは語彙だ。広告への割当は動く。

### 入室履歴を複数の幅でまとめ、注文履歴は別に読む
IAGは軽量TransformerであるLazy Decoderを使う。MSIでは直近の入室列をstride 1,2,10で連続ブロックへまとめ、それぞれ射影と位置表現を加える。stride 10は10件ごとに1件を抜く説明ではなく、10件を連結して一つの表現を作る式である。like、cart、orderは別ストリームとして符号化し、入室の複数スケールと長期profileに連結する。

`Pθ(y|M_u(t)) = Π_l Pθ(s_l | s_<l, M_u(t))`

MF-NTPはどのログを強く学ぶかを決める。

`w(x) = w_feedback(x) · w_user(x) · w_eCPM(x)`

`L_NTP = −[Σ_x w(x) Σ_l γ_l log Pθ(s_l|s_<l,M_u(t_x))] / [Σ_x w(x) Σ_l γ_l]`

feedbackは閲覧後の深い行動、userは価値層、eCPMは分位で正規化した商業価値を表す。実装では重みを正規化・clipする。将来の行動は学習時の重みにだけ使い、リクエスト時の入力へ漏らさない（Eq. (5)）。

### IOPOは候補の鮮度と更新頻度を分ける
warm-upではNTPとReward Modelを学ぶ。その後は現方策で候補群を生成し、短いGRPO更新をT stepごとに行う。間のstepではログに対するNTPを続ける。BA-GRPOは行動への一致を、VA-GRPOは商業価値を加える。候補群内の報酬を平均と標準偏差で正規化し、clipしたadvantageをlog方策確率へ掛ける。

`r_va = r_post + β_va r_eCPM`、`A_va = clip((r_va − μ_va)/(σ_va+ε))`

Reward Modelは下層のLSID embeddingを共有する。post-exposure LREは実ユーザーfeedback、eCPM教師は本番fine-ranking scoreである。報酬計算ではstop-gradientを使う。したがって商業価値の信号は既存ランカーにも依存する。

サービングはbeam searchで256個のLSIDを生成し、稼働中LiveIDへ解決して下流filtering/rankingへ渡す。静的SIDを扱う[GLIDE](glide-spotify-sid.html)や[Gryphon](gryphon-ilsm.html)との比較点は対象の変化であり、[TGR](tgr.html)と同様に置換範囲を明示して読む。

[一次資料：§2–3、Eq. (1)–(14)、Figure 4](https://arxiv.org/html/2608.24034)。

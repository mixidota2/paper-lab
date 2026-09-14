### ユーザー文脈、生成軌跡、候補属性を順に置く
ユーザー側は動画・ライブなどの履歴とプロフィールを、種類別のprojectionとtype embeddingでtokenへ変換する。候補SIDには3層のRes-Kmeansを使い、codebook sizeは原文どおり8129と記される（§3）。SIDの入力は `[BOS, q1, q2, q3]`。BOSからq1、q1からq2、q2からq3を予測する。末尾q3は予測用ではない。全軌跡を見た状態をランキングへ渡す。

`S = [P_history ; P_profile ; T_gen ; T_rank]`

候補側のT_rankにはitem profile、content embedding、ユーザー×候補の交差統計、上流の事前スコアなどを投影して置く。これらをqueryとして層ごとに更新する。原典はオンライン構成に3層・hidden dimension 640を採用する（§6.3.3）。

### DQ-PCAは二つのqueryに別の範囲を見せる
生成queryはすべてのユーザー文脈と、その位置までの生成tokenを読む。maskは下三角で、自己位置を含む。位置iの出力から次tokenを予測する。候補特徴は読めない。ランキングqueryが読むのはプロフィール、全SID軌跡、全item-feature tokensである。長い履歴は直接読まない。候補依存の履歴検索結果などは候補側tokenへ含める（式7–10）。

`Q_gen = T_gen,  K_gen = V_gen = [P, T_gen]`（生成部分はcausal）

`Q_rank = T_rank,  K_rank = V_rank = [P_profile, T_gen, T_rank]`（範囲内は双方向）

Wq/Wk/Wv/Woのbase射影を共有し、FFNは生成用とranking用を分ける。プロフィールとSIDの表現を前向き計算で共有することと、同じ損失で全層を更新することは別である。

### stop-gradientの先にranking専用の適応経路を残す
生成損失は `L_gen = −Σ_i α_i log p(q_i | u, q_<i)`、αは前の階層ほど大きい。ランキング入力は `z = Concat(u, v, h_lastSID, h_rank)` で、元のユーザー・author特徴も残す。MMoE（タスクごとのgateが複数expertを混合するモデル）とタスク別towerで予測し、`L_rank = Σ_t ω_t BCE(ŷ_t, y_t)` を最小化する（式12–15）。

rankingのQ/K/Vでは `X_rank = sg(WX) + B_rank A_rank X` とする（式17）。sgはbase経路への逆伝播を止め、低rank行列BとAがranking側の変化を担う。生成経路ではこのLoRAを使わない。ranking側FFNとtowerも学習対象になる。原典は生成用・ranking用のパラメータ集合を分けつつ、疎なembedding集合は共有すると記す（式18）。本Labでは「全パラメータが完全隔離」とは説明しない。

### 二段階学習はSID表現が安定してから識別を加える
第1段階は生成損失のみ。第2段階はそのcheckpointから始める。同じ系列にranking損失を追加する。rankingには全sample streamを見せ、各タスクの意味に合うsample maskを掛ける。生成側はクリックを残し、露出をrandom samplingして分布学習に使う。先にSIDの意味を安定させるのは、変動する表現をもとにランカーが誤った識別境界を学ぶのを避けるためだと著者は説明する（§5.1）。

### 一つのサービスでも候補属性の取得は残る
GPUにユーザーprefixと候補別SID軌跡の層別KVを保持する。CPUが候補属性を取得した後、ranking tokensを追加し、cached statesとranking側LoRAを使って候補をまとめて採点する。ranking queryはここでも履歴全体へ戻るわけではない。strategy filterとrankingは候補集合を複製して並行実行し、最後にfilter flagを適用する。待ち時間にrankingを重ねる設計だ（Figure 3）。

[OneRanker](oneranker-ads.html)は生成とrankingのKV共有に加え、DCでranking側の選好を生成へ戻す。[Gryphon-v2](gryphon-v2-cascade.html)は全カスケードの置換を主題とする。UniR²で確認すべき問いは、同一系列での表現融合がrecall＋pre-rankの境界をどこまで改善したかである。

[一次資料：arXiv v1](https://arxiv.org/pdf/2607.24439v1)

### 3段のSIDを出すencoder–decoderに、行動のprefixを足す

商品を残差量子化した3つのtokenで表す。各codebookは8192、ユーザーの短期履歴・長期履歴・profileをencoderへ渡す。decoderはscene指示Iₛ、近傍時間でLLMが作るreasoning埋め込みIᵣ、行動指示Iᵦを読む。オンライン構成は3Bパラメータ中1Bが活性化するMoEである。[§3、Appendix G](https://arxiv.org/html/2607.24255v1#S3)

Iᵦは自然言語の自由入力ではない。click・cart・orderに予約tokenを割り当て、共通embedding tableから読み、2層の射影ψを通す。Appendix B.2ではLeakyReLU（負側0.01）とdropoutを使う。prefixは[BOS, Iₛ, Iᵣ, Iᵦ]。学習時は実ログの行動、配信時は面の目的を指定する。

### 露出だけのtargetを除き、行動と教師信号をそろえる

重複行動の優先順位はorder > cart > click > exposure。各targetを展開し、露出だけの例を落とす。既定の重みはclick=1.2、cart=1.5、order=2.0である。listwiseではN個の商品をL=3N tokenへ展開する。式6の幾何重みは平坦化したt全体に掛かる表記であり、このLabでも商品ごとに重みをリセットしない。

### 同じモデルでも、教師だけが未来を読む

教師は同じbackboneへFを追加する。Fはtⱼ>t₀を満たす未来targetから最大2商品、各3 tokenを採り、固定6 tokenへpaddingする。studentにはFを渡さない。教師側の予測位置は6 token分のoffsetを合わせる。Appendix Eの表10はexposureをdefaultと記すが、表3で良いのはexposure-onlyを除いたClick版である。default表記と最良結果を同一視しない。

疎な一致報酬で最良軌跡を選び、その軌跡上で教師を評価する。teacherのentropy Hᵀ<0.75ならSD、Hᵀ>2.6ならforward KL。中間帯と閾値に等しい点には、該当する蒸留を掛けない。高entropyを単に捨てる設計ではない。[式5–13、Algorithm 1](https://arxiv.org/html/2607.24255v1#S4)

### 指示のprobeは「注文だけ指定すれば万能」を否定する

下表は同じ評価文脈に異なるIᵦを強制した結果。orderを強制するとorder部分集合を保つ一方、click部分集合のHR@512は42.99から34.54へ下がる。目的を変えた結果なので、全ユーザーへorder指示を固定する根拠にはならない。Figure 4のLDAは行動ラベルを使った射影であり、教師なしで自然に分離した証拠とは区別する。

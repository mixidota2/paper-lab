### 1段目はカテゴリ、残り2段は残差の近さで決める

CQ-SIDはRQ-VAEを土台とし、1,711の有効カテゴリを最初の量子化に使う。既知カテゴリの商品はそのカテゴリIDを強制的に選び、未知の場合は最近傍codeへ割り当てる。codebookは2048×1024×1024。第2・第3段は残差の最近傍を取り、EMAで更新し、使われないcodeをrestartする。

query-itemの双方向InfoNCEを加え、再構成誤差＋commitment＋対照損失で学習する。実験設定はβ=1、γ=0.001、温度τ=0.1。queryのない商品では対照項をmaskする。意味の近い商品を同じSIDへ集めるため、一意IDは要求しない。[式1–7](https://arxiv.org/pdf/2605.14434v1)

50商品を超すSIDは、G=min(ceil(c/50),100)の群へランダム分割し、第3段へgroup suffixを付ける。これは上限100群のため、必ず各群50以下になる保証ではない。語彙の残差量子化と、この後処理の群分割は別工程だ。

### Qwen2.5-0.5Bを3段階のSFTからEG-GRPOへ進める

商品title→SID、query→SID、user+query→SIDの順にSFTする。query段ではクリック・購入に対応するSIDを3つsample。個人化段では性別・年齢帯・関連カテゴリの最近のクリックSIDも入力する。最後に既存rankingとの整合を狙うEG-GRPOを行う。

報酬は購入またはクリック1.0、露出のみ0.5、有効SIDのみ0.1、無効0。順位の上から最初に該当する条件を使い、加算しない。通常8出力の群へ、クリックまたは露出集合からK個の正解SIDをpseudo-generated outputとして注入する。広げた群で平均・標準偏差を計算し、clipped policy gradientへ入れる。expertはオンラインに正解を渡す仕掛けではない。[式8–10、Algorithm 2](https://arxiv.org/pdf/2605.14434v1)

式10の掲載式にはKL項がない一方、§4.1の設定はKL weight=1.0と記す。完全な学習lossやoff-policy注入の補正を再構成できたとは扱わない。

### 日次の商品集合と既存rankingが残る

数億商品の全量から効率の良い約2,100万商品を選び、SID-to-items lookupを作る。新しい商品を日次でクラスタに追加する。生成されたSIDを商品へ展開し、既存の複数召回チャネルとrankingへ渡す。40msはこの配置での平均値だ。

[OxygenREC-v2 Lab](oxygenrec-v2-idgr.html)は行動指示と未来情報を使う教師からの蒸留が主題で、expert SIDを群へ注入する本論文とは教師信号の入れ方が違う。[TSGR](https://arxiv.org/abs/2607.18796)は表現・候補順位に価値を入れ、[CRID](https://arxiv.org/abs/2607.11392)はclusterと群内business-value順位をDocIDへ符号化する。本論文の「群を呼んで既存rankingへ渡す」判断と比較できるが、同条件の直接比較結果ではない。

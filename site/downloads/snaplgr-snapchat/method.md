### Qwen3-VLでSIDを作り、Qwen3-0.6Bで生成する
動画のmultimodal表現はQwen3-VL-Embedding-8Bの4,096次元中、先頭1,024次元を使う。Matryoshka表現のprefixを利用する。RQ-VAEは3段のcodebook（1,024、512、256）を持ち、全codebookへのstraight-through勾配、reconstruction、commitmentを使う。

user–video二部graphの2-hop近傍でPersonalized PageRank（PPR）を求め、co-engagement上位pairをInfoNCEの正例にする。productionではP75閾値。PPRは πᵢ=(1−α)eᵢ+αPᵀπᵢ で、anchorへ戻る項が近傍を保つ。

LLMのCPTでは新しいSID embeddingだけを学習し、凍結したLLMへSIDから動画descriptionを出させる。SFTではChatMLの履歴からfuture SIDを学習し、assistant tokenだけにlossを掛ける。

CPTは初期に1回、SFTは1時間ごとの増分学習。

<figure class="teaching batch21"><h3>毎日生成し、オンラインではindexを読む</h3><div class="b21-serving"><section><h4>Offline / daily batch</h4><p>履歴SID → Qwen3-0.6B</p><p>TensorRT-LLM / beam 32</p><p>SID → value-weighted動画展開</p><p>user–video indexへ保存</p></section><section><h4>Online / request</h4><p>user ID → serving index</p><p>候補動画を取得</p><p>既存rankingへ渡す</p><p>最終response</p></section></div><figcaption>原典 Fig. 2・§2.3。SFTはhourlyだが、候補のbatch生成はdaily。オンラインrequestごとにLLMをdecodeする図ではない。</figcaption></figure>

materializationはSIDごとの動画集合を V(i)=Σₘ wₘ Sₘ(i) で並べ、固定上限まで保存する（Appendix A.3）。Sₘはengagement指標の推定率。SID hitとvideo hitを分ける理由がここにある。

### 高速化の分母を固定する
TensorRT-LLMでbeamの拡張、score、KV管理をCUDAへ移す。Parquet shardを各workerが自分で取得し、中央driverのfan-outを外す。prefetchと非同期writeを重ねる。論文の45.7倍は旧Python・中央集約基盤からの累積samples/s/GPUの比で、推薦request latencyの45.7倍改善ではない。

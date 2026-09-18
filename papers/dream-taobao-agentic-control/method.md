### Intent Engine：何を欲しいかと、どう選ぶかを分けて持つ

L0 Physicalは長期的なプロフィール、L1 Demandは需要category・場面・意図の確信度、L2 Preferenceはbrand・価格・属性・意思決定段階など。たとえば同じ家電の需要でも、比較中なのか購入直前なのかで優先すべき情報が変わる。L0は複数intentに共有し、L1とL2を行動に応じて更新する（§3.2）。

全eventで重い推論を回すわけではない。端末のF1は60種類超の行動を特徴へ圧縮し、F2は7次元の離散特徴を単層GRUで追って変化点を検出する。2秒以内に元画面へ戻るなどの誤tapを抑え、モデルが使えない場合はRuleTreeへ戻す。F3は最大50 eventのID中心のpackを送信。F4はcloudでitem名やcategoryを復元し、既存intentとの差から推論へ進めるかを判定する（表1）。

F2の送信率は約15%、全体の報告量は元の約8.7%という著者報告。後段の各段階の実測通過率は提示されていないため、15%から8.7%への図は個々のgateの効果分解ではない。6.3%の非同期4Bへのrouting率は別の母集団の値であり、8.7%に足さない。

推論は同期0.8B Main Agentが差分insert/updateを出し、複雑なcaseを非同期4Bのcontext / domain expertへ回す。4B Dreamingは夜間のidle計算で記憶を整理する。大きいagentの分布からMain Agentへのon-policy distillationも記載される。Intent側の各checkpoint名を推定して補わない。MetaModelについてはQwen3ベースと明記され、付録Bは4B MetaModelのreplay-RLを評価する。

### Meta Engine：LLMの意味的な提案を、型のある設定に変換する

M1はintentの要約、目的、購買力、活動groupを整理する。M2はStrategy Memoryを参照してschemaに従うJSONのstrategyを作る。たとえばranking_weight_boost、category_preference、experience_constraints。M3はTool Processによる決定的な変換結果であり、自由文のLLM出力ではない（§4.2）。

MetaModelはnearlineで最新の有効bundleをcacheに書く。request時にはTool Processが版・schema・期限を検査し、許可されたfieldだけをretrieval、ranking、rerankingへ配る。同じcategoryの好みもretrievalでは候補quota、rankingではscatter幅、rerankingでは構成比として解釈する。既存cascadeのモデルと推薦リスト生成器は残る。LLMがitem IDや最終順列を直接出す構造ではない。

rankの目的ごとのsemantic level bは−2から2。元の重みw⁰と掛けたδを使って、校正済み予測値v̂の項を補正する。categoryのscatter幅はmax(1,既定値+b)。business supportは許可PlanIDだけで件数上限も守る。JSON、schema、allowlist、値域のどれかが失敗したらdefaultへ戻す。未実装のcontent-type levelはno-opとされるなど、意味的な提案のすべてに実行権があるわけではない。

### 呼び出し頻度も、報酬の学習経路も分ける

§4.1はintent更新の価値Δから費用・遅延を引き、groupと時間帯の呼び出し予算を守る問題として定式化する。Δはonlineでは分からないため、行動分布のJensen–Shannon divergence、活動量、時刻などを正規化し、context別の閾値で代用する。式13は本文が4信号と述べる一方、表示された和は3項で重みの総和は4項になっている。このLabでは欠けた項を推定せず、toyのscoreを手入力する。

Reward Dual Loopのoffline側は、本番経路の隔離replay。logの同じrequestに対し、defaultとstrategyを別々のservice callでK回ずつ評価し、最終listをEvaluatorが採点する。平均strategy scoreが平均default scoreを上回ったときだけ報酬1、それ以外0。差の大きさは診断用に残すが、学習報酬は二値である（式20–25）。

online側は実際のclick・取引を観測し、Evaluatorの校正やStrategy Memoryの経験蓄積へ返す。replayは実行時のfeatureやmodel stateを使うため、過去の環境の厳密な再現ではない。繰り返し平均はnoiseを減らしてもproxyの誤りを消せない。最終的なbusiness impactはonline A/Bで判断する。
<figure class="teaching batch18"><h3>制御を重ねる位置：設定は変わるがcascadeは残る</h3><div class="b18-plane"><div class="b18-control"><strong>nearline control plane</strong><p>L0 / L1 / L2 → M1 要約 → M2 strategy + Memory → cache</p></div><p class="b18-arrow">↓ request時にM3へ変換・検査</p><div class="b18-cards"><div><strong>retrieval</strong><p>許可categoryのquotaや供給種別を調整</p></div><div><strong>fine ranking</strong><p>既存scoreの項・scatter・PlanID保護を補正</p></div><div><strong>reranking</strong><p>既存Generatorの密度・除外・位置規則を設定</p></div></div><p>失敗・期限切れ → 各stageのdefaultへ</p></div><figcaption>図1・7、式16。構成を教えるための再描画。LLMはrequest時の最終順列を生成しない。</figcaption></figure><figure class="teaching batch18"><h3>Intent funnel：元の行動量を100として読む</h3><div class="b18-funnel"><div style="--w:100%">F1：端末で符号化　100</div><div style="--w:65%">F2・F3：変化点 → pack送信　約15</div><div style="--w:45%">F4：cloudで復元・admission　全体約8.7</div></div><p>幅は説明用。15と8.7は著者の近似値。各gateの独立したA/B効果ではない。</p><figcaption>§2–3.1・表1。8.7%は元の約8.7%まで絞ったという意味で、8.7%削減ではない。</figcaption></figure>

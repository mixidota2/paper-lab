### promptとresponseを同じtoken空間に置く

§2・図1。履歴は作品ID、行動種別、経過時間bucket、継続時間bucketへ分ける。言語・profile種別、device・時間帯も専用tokenにする。長すぎるimpression履歴には手作業の要約が残る。ページ側は行ID→作品IDの繰り返しで、左から右、上から下へ並べる。paginationでは前回の行と最新反応を文脈へ追加する。

§4のモデルはdecoder-only Transformer。入力embeddingと出力projectionを共有しない。softmaxを使う事前学習とsigmoidを使うWBCで適切なlogit尺度が異なるためだ。オンラインモデルは約200M parameters。

### NTP、WBC、RLは目的が異なる

事前学習は好意的な反応を得たproductionページのnext-token prediction。以下は本文の説明を記号化したもので、原論文に番号付きで掲載された式ではない。

`L_NTP = −Σ_t log pθ(y_t | context, y_<t)`

WBCでは報酬rの符号から二値ラベルb、絶対的な大きさから重みwを作り、該当tokenのlogit zに対して `L_WBC = −Σ w[b log σ(z) + (1−b)log(1−σ(z))]` を最小化する。露出した行にも作品報酬を集約したtargetを付け、追加のランダム負例も使う（§5.2）。

RLはDr. GRPO、verl、vLLMを使用。実反応を数値化するreward systemと、未配信ページの価値を予測するTransformer reward modelを区別する。policyとreferenceは事前学習checkpointから初期化し、KL罰則で元の分布から離れすぎないようにする（§5.3）。オンラインで評価したのはWBCだけである。

### 業務制約と更新周期を推論に組み込む

`z′_v = z_v + m_v`、適格なら `m_v=0`、不適格なら `m_v=−∞`。位置固定、重複除去、行カテゴリとの整合を各stepで強制する（§6.3）。候補集合の存在とmaskの存在は両立する。

hybrid row decodingは先頭の数作品だけ逐次生成し、残りを一回のforwardから得たscoreで選ぶ（§6.4）。行末の各作品が直前の全作品に条件付くわけではない。日次の継続学習は最新データと過去データを混ぜ、大きな学習更新を別周期で行う。新作品にはcontent embeddingとの融合、metadataの文脈注入、fallback tokenを使う（§6.1–2）。

出典：[2606.31031v2](https://arxiv.org/pdf/2606.31031v2)。上記で「Lab」とした式・条件は説明用の補助である。

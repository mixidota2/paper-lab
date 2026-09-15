### 再構成だけでなく、協調関係と衝突を同時に学ぶ

shared encoder fθがmultimodal特徴xᵢをzᵢへ写す。残差量子化器が各層のcodeを選び、量子化ベクトルの和からdecoder hφが元特徴を再構成する。離散選択にはstraight-through estimator（順伝播は離散、逆伝播は連続の近似）を使う。これにSwingで作ったtrigger–target正例のdual-tower contrastive学習を加える。[§4.1](https://arxiv.org/html/2603.00632v1#S4.SS1)

産業側の特徴は説明文、ASR transcript、key-frame画像をmultimodal LLMで埋め込む。具体的な産業encoder名は本文では特定されない。offlineのSentence-T5-XXLと同一だとは仮定しない。

### CVPMは2種類の良い重なりを除く

B個のtriggerを先に、対応するB個のtargetを後に並べる。iとi+Bの構築正例を除外し、同一IDの全出現組も除く。後者は自己pairと重複サンプルを含む。ここで使うHaMR用maskと、InfoNCEで同じtrigger IDの偽負例を除くmaskは用途が異なる。どちらもMという記号が使われるが、同一配列として実装しない。

残ったpairを完全衝突H=0と、0<H≤Rの部分衝突へ分ける。offlineはR=1、onlineはR=2。半径内でHが1から2へ変わるたびに連続的な係数を掛ける式ではなく、完全・部分の2群でmarginと重みを切り替える。[§4.2、Appendix A.2](https://arxiv.org/html/2603.00632v1#S4.SS2)

### 幾何マージンは一意のSIDを直接割り当てない

正規化embedding間のcosine距離D=1−eᵢᵀeⱼがmargin未満なら反発する。mfull=.8、mpartial=.5なので、完全衝突の方が大きく離す。HaMRは連続空間を変えて次の量子化を促す。lossが0でも、固定codebookの境界を必ず跨ぐとは限らない。有限のコード空間で一意性を保証する構成規則とは別の仕組みである。

### 既存Labとの接点は、異なる介入位置にある

| 手法 | 主に変える場所 | QuaSIDとの違い |
| --- | --- | --- |
| [ISD](understanding-sids-isd.html) | 固定SIDのbeam探索へ外部順位を注入 | tokenizerの衝突学習は変えない |
| [GR4AD / UA-SID](gr4ad-ads-generative.html) | 意味コードに業務上のhash識別を加える | 有限hashには再衝突があり、mask付き反発とは異なる |
| [TAGR](tagr-live-sid.html) | 固定語彙への割当を時間変化に合わせて更新 | 主眼はライブ内容の鮮度。QuaSIDは反発を掛ける組を選ぶ |
| [CRID](https://arxiv.org/abs/2607.11392) | semantic clusterとbusiness-valueの順位でDocIDを構成 | cluster内の順位で区別する設計。一意IDの構成と幾何正則化を分ける |

この比較は読書メモであり、QuaSID論文のhead-to-head比較ではない。Labの次の検証案は、同じ候補予算で有害pairの識別精度、残存衝突、推薦品質を一緒に測ること。SID entropyだけを採択指標にしない。

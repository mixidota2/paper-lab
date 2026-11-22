### 先頭の2トークンは商品の意味、最後の1トークンは同じ組での順位

カテゴリやブランドを含む商品embeddingを、RQ-VAEの商品エンコーダーに渡す。第1コードが説明しきれなかった差（残差）から第2コードを選ぶ。(s₁,s₂) が商品の意味を表す先頭部分（prefix）。検索語を処理するquery encoderは、トークン化の学習時だけ使う。再構成・commitmentの損失に双方向InfoNCEを加え、同じminibatch内で検索語と商品を対応づける。各コード表と第3トークンの語彙数は8,192。

第3トークンrには、そのprefix内の順位を割り当てる。EB-CVRを先に比べ、同値なら行動funnel値、GMV、item IDの順に比べる（Eqs. 3–5）。初期は1商品1識別子とする。EB-CVRで使う比率の分子は、購入数bと、重みを掛けたカート追加数ηₐaの和。分母はクリック数cとする。事前値（prior）はΣ(b+ηₐa)/Σc。

### 商品情報から始め、検索する人と履歴も使って識別子を学ぶ

Qwen2.5-0.5B-Instructに識別子（SID）を段階的に学ばせる。Stage 1は商品内容、Stage 2は検索語を入力する。Stage 3はユーザー・検索語・履歴を使い、履歴には直近3検索と長期の関心の要約を含める。この段階では検索語と商品の組のEB-CVRを重みとし、SIDの段ごとにも損失の重みを付ける。第2段が予測しにくいため、α₂>α₁>α₃とする。LO-SFTでは正解への通常の損失を残し、半径3・温度1・係数0.02で、正解に近い順位にも教師分布の確率を配る。学習のたびに全商品の順位を付け直す操作ではない。

### Prefix-GRPOは、識別子の形式と商品が入っているかを先に確かめる

1つのpromptから8応答を生成する。書式が不正なら−2、どの商品も割り当てられていないslotなら−1とし、それ以上は加点しない。形式が正しく商品があるときは、購入3、クリック1、露出0.1のうち、該当する行動で最も高い点だけを使う。同じリクエスト内でranker scoreを標準化する。平均より高い場合にだけ、標準化した偏差をtanh関数に通し、算出した報酬を最大0.2まで足す。行動が一致しないSIDに限り、関連性grade 3/2/1に+0.08/+0.03/−0.10を与える。行動と関連性を両方加点するわけではない。

同じpromptからの応答群で報酬を標準化し、whiteningとclipの後のadvantageを各トークンに配る。第1トークンの重みは1。第2・第3トークンは、次に選べる子の数の対数で0.1〜1に重み付けする。PPO型clip、負のadvantageへのdual clip、SFT参照policyとのKLの係数0.8を使う。重みを掛けるのは方策を学習する損失で、推論時のlogitではない。

### 日次は既存の識別子を維持し、月次は履歴も作り直す

日次更新では、既存のSIDを変えない。新商品には、同じprefixにある過去の割り当てから順位が近いslotを選ぶ。上限を超えた場合は末尾のslotを共有する。共有SIDは対応する商品すべてに展開し、最終順位付けに渡す。日次学習には、行動時点のSIDラベルと過去のデータの再利用（historical replay）を使う。検証後、モデル・探索木（Trie）・商品との対応表（map）を一組として同時に切り替える。月次の再構築は別の主要バージョンとして扱い、そのバージョンで履歴を符号化し直して再学習する。

オンラインのbeam幅は(20,50,500)。カタログに商品が割り当てられている経路だけをTrieで探索する。生成した商品と通常経路の候補が重複していれば除き、最終順位付けに渡す。

<figure class="teaching" data-b21><h3>新商品Dの到着を追う</h3><label>住所方策 <select><option value="0">初日</option><option value="1">全並べ替え</option><option value="2">固定更新</option></select></label><div data-output aria-live="polite"><p>初日：A/B/Cに一意な住所</p><div class="matrix-scroll" tabindex="0"><table><tr><th>商品</th><th>第3 token</th></tr><tr><td>A</td><td>0</td></tr><tr><td>B</td><td>1</td></tr><tr><td>C</td><td>2</td></tr></table></div></div><script type="application/json" data-frames>["<p>初日：A/B/Cに一意な住所<\/p><div class=\"matrix-scroll\" tabindex=\"0\"><table><tr><th>商品<\/th><th>第3 token<\/th><\/tr><tr><td>A<\/td><td>0<\/td><\/tr><tr><td>B<\/td><td>1<\/td><\/tr><tr><td>C<\/td><td>2<\/td><\/tr><\/table><\/div>", "<p>全並べ替え：旧B/Cの住所が変わる<\/p><div class=\"matrix-scroll\" tabindex=\"0\"><table><tr><th>商品<\/th><th>第3 token<\/th><\/tr><tr><td>A<\/td><td>0<\/td><\/tr><tr><td>D<\/td><td>1<\/td><\/tr><tr><td>B<\/td><td>2<\/td><\/tr><tr><td>C<\/td><td>3<\/td><\/tr><\/table><\/div>", "<p>固定更新：B/Dが共有し、旧住所を守る<\/p><div class=\"matrix-scroll\" tabindex=\"0\"><table><tr><th>商品<\/th><th>第3 token<\/th><\/tr><tr><td>A<\/td><td>0<\/td><\/tr><tr><td>D<\/td><td>1<\/td><\/tr><tr><td>B<\/td><td>1<\/td><\/tr><tr><td>C<\/td><td>2<\/td><\/tr><\/table><\/div>"]</script><figcaption>run.pyの人工4商品で、商品と第3トークンの対応だけを変えた。モデルを学習させた結果ではない。</figcaption></figure>

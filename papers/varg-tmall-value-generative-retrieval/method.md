### 意味の2 tokenと、価値順の1 tokenを分ける

商品embedding（category・brandを含む）をRQ-VAEのitem encoderへ入れる。残差量子化の第1 codeを引いた残差から第2 codeを選び、(s₁,s₂)を意味prefixにする。query encoderはtokenizer学習時だけ使う。再構成・commitmentに双方向InfoNCEを足し、同じminibatchのquery–item対応を揃える。各codebookと第3語彙は8,192。

第3 token rはprefix内でEB-CVR、行動funnel値、GMV、item IDの順にtie-breakして付ける（Eqs. 3–5）。初期は1商品1住所。分子は購入数bと加重cart数ηₐaの和、分母はclick数c。priorはΣ(b+ηₐa)/Σcとする。

### Qwen2.5-0.5B-Instructへ段階的に住所を教える

Stage 1は商品内容→SID、Stage 2はquery→SID、Stage 3はuser・query・history→SID。Stage 3には直近3検索と長期関心要約、query–itemのEB-CVR重み、level別lossを入れる。level 2が主な予測障害なのでα₂>α₁>α₃。LO-SFTは正解tokenへの通常lossを残し、半径3・温度1・係数0.02で近いrankにも滑らかな教師分布を与える。学習が進んでも全順位を作り直す操作とは違う。

### Prefix-GRPOはまず報酬を受け取れる住所か調べる

1 promptから8応答を生成。書式外は−2、未占有slotは−1で打ち切る。合法・占有済みなら購入3、click 1、露出0.1の最高行動だけを採用する。要求内のranker scoreの正の標準化偏差にtanhをかけて最大0.2の報酬を足す。行動一致がないSIDだけ関連性grade 3/2/1に+0.08/+0.03/−0.10を与える。行動と関連性を二重加点しない。

同prompt群で報酬を標準化し、whitening・clip後のadvantageをtokenへ配る。第1 tokenは重み1、第2・第3は合法な子の数の対数で0.1〜1に重み付け。PPO型clip、負advantageのdual clip、SFT参照policyへのKL係数0.8を使う。ここでの重みは推論logitの補正ではなくpolicy lossの係数である。

### 日次の互換性はmodel・Trie・mapの組で守る

既存SIDを固定し、新商品は同prefixの順位に近い歴史slotへ割り当てる。上限を超えれば末尾slotを共有する。共有SIDを商品集合へ展開し、最終rankerへ渡す。モデルは行動時点のSIDラベルとhistorical replayで日次学習。検証後にmodel・Trie・mapを原子的に公開する。月次rebuildは別primary versionとして履歴もre-encodeし、再学習する。

オンラインbeam幅は(20,50,500)。Trieはカタログ内の占有pathだけに制約し、生成商品を通常経路の候補と重複排除してfinal rankerへ渡す。

<figure class="teaching" data-b21><h3>新商品Dの到着を追う</h3><label>住所方策 <select><option value="0">初日</option><option value="1">全並べ替え</option><option value="2">固定更新</option></select></label><div data-output aria-live="polite"><p>初日：A/B/Cに一意な住所</p><div class="matrix-scroll" tabindex="0"><table><tr><th>商品</th><th>第3 token</th></tr><tr><td>A</td><td>0</td></tr><tr><td>B</td><td>1</td></tr><tr><td>C</td><td>2</td></tr></table></div></div><script type="application/json" data-frames>["<p>初日：A/B/Cに一意な住所<\/p><div class=\"matrix-scroll\" tabindex=\"0\"><table><tr><th>商品<\/th><th>第3 token<\/th><\/tr><tr><td>A<\/td><td>0<\/td><\/tr><tr><td>B<\/td><td>1<\/td><\/tr><tr><td>C<\/td><td>2<\/td><\/tr><\/table><\/div>", "<p>全並べ替え：旧B/Cの住所が変わる<\/p><div class=\"matrix-scroll\" tabindex=\"0\"><table><tr><th>商品<\/th><th>第3 token<\/th><\/tr><tr><td>A<\/td><td>0<\/td><\/tr><tr><td>D<\/td><td>1<\/td><\/tr><tr><td>B<\/td><td>2<\/td><\/tr><tr><td>C<\/td><td>3<\/td><\/tr><\/table><\/div>", "<p>固定更新：B/Dが共有し、旧住所を守る<\/p><div class=\"matrix-scroll\" tabindex=\"0\"><table><tr><th>商品<\/th><th>第3 token<\/th><\/tr><tr><td>A<\/td><td>0<\/td><\/tr><tr><td>D<\/td><td>1<\/td><\/tr><tr><td>B<\/td><td>1<\/td><\/tr><tr><td>C<\/td><td>2<\/td><\/tr><\/table><\/div>"]</script><figcaption>run.pyの人工4商品。変わるのはmap。モデルの学習効果は含まない。</figcaption></figure>

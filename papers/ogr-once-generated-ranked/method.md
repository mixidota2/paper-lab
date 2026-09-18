### TUSID：意味と共起を、量子化する前にまとめる

動画の画像・音声・文章をMLLMで符号化し、Brand、Category、供給側のB-tags、需要側のC-tagsを共有text encoderで符号化する。MLLM側をqueryとするcross-attentionで属性を集約し、sigmoid gate付き残差として足す。単純な平均ではなく、動画ごとに属性の寄与を調節する。これをSASRecのitem embeddingとして使い、次item予測損失と残差のL2正則化で融合部を学習する（式2–4）。MLLMとtext encoderの具体的な製品名・checkpointは確認範囲では示されていない。

次に、正の反応を含む学習prefixだけから近傍共起を集める。中心item iの周囲ω=5以内にあるjを、距離の逆数1/|p−q|で重み付けする。CountSketch-based Collaborative Encoding（CCE）は、共通hash hと符号hash σを使ってこの疎なitem間関係を256 bucketへ圧縮する。符号付きlog変換、正規化、固定random projectionで128次元へ移す。検証・testの履歴を混ぜないことが前提になる。

同じitemに寄与した異なるユーザー数Uを数え、Confidence-Aware Weighting（CAW）で協調枝の重みαを抑える。同じユーザーの反復はsketch量を増やし得るが、Uは1人として数える。意味枝と協調枝を各々正規化し、√(1−α)と√αで重み付けして連結する。α上限は0.35、τ=0.5。最後にRQ-KMeansで4段・各1,024 codeのSIDに量子化する。U=0では意味枝だけが残る。共起の強さと信頼度を別々に扱う設計である。

### GL2P：表示順を計画してから、各位置のSIDを並行して伸ばす

履歴encoderは4層・8 head・hidden 512、FFN 2,048。最大履歴128件のSID embeddingを深さ方向に足し、時間embeddingを加える。List-Wise Preference PlannerとPosition-Wise SID Decoderはそれぞれ2層・8 head・hidden 512、FFN 2,048。plannerはcausal attentionで先行位置を参照し、履歴にはcross-attentionする。decoderのbeam幅は20（表10）。

学習時は正解SID embeddingの合計を右へずらしてplannerへ入れるteacher forcing。推論時は前の位置の潜在表現pを次へ渡すため、itemの全SID確定を待たずに次の位置を計画できる。位置mのpが出たら、その位置のD tokenを自己回帰で復号する。異なる位置のSID鎖はpがあれば並行処理できるが、同じSID内の深さ方向は直列のまま。

露出順と反応順の2種類の教師slateを使い、Lsup=Lsid,exposure+0.3 Lsid,feedbackで学ぶ。出力はすでに順序を持つslateなので、候補を別rankerへ渡して初めて表示順を得る「generate then rank」と責務が違う。生成先の全itemを無条件に利用できる保証や、無効SID処理の詳細までは示されていない。

### SPA：補助報酬が主目的を逆転させないようにする

主報酬は位置ごとの有効視聴+0.10、完視聴+0.15、like+0.20、share+0.15、即skip−0.15、dislike−0.25のslate平均。補助報酬は意味的多様性0.90と新規性0.10。ユーザー内の候補集合で各報酬を平均0・分散1に標準化し、主と補助の符号が一致する場合だけ補助を加える（式15）。補助の値が大きいという理由だけで主報酬の向きを反転させない。

学習は参照policyとの尤度比をclipし、候補分布のKLと教師データのreplayも加える。clip幅0.1、KL重み0.05、replay重み0.1。更新するのはplannerとSID decoderで、他は固定する。これは報酬への過剰適合を抑える設計だが、報酬そのものの妥当性までは保証しない。

**付録5の限定が重要。** 本文のCandidate Rolloutsはbeamでslateを組み立てる説明だが、実験で報酬を校正する集合Aは露出log内の完全なslateだけと付録が明記する。未露出・反実仮想のslateに観測反応を割り当てない。ユーザーに2つ以上のlogged slateがない場合は除外し、一定値の報酬成分は標準化後0にする。このLabも、未露出slateの報酬を作らない。
<figure class="teaching batch18"><h3>融合する場所を追う</h3><div class="b18-cards"><div><strong>意味枝：学習する</strong><p>MLLM → 属性cross-attention → gate残差。SASRec損失で推薦向けに調整。</p></div><div><strong>協調枝：学習prefixから集計</strong><p>近傍共起 → signed CountSketch → signed log → 正規化 → 固定射影。</p></div><div><strong>CAW → RQ-KMeans</strong><p>distinct usersでαを決め、重み付き連結後に4段SIDへ。</p></div></div><figcaption>図2、式2–7、付録4・表9を説明用に再構成。MLLMの名称は補っていない。</figcaption></figure>

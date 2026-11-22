### SIDで候補を出し、対応する曲をそれぞれ採点する

重みを固定したQwen2.5-Omniで、曲の先頭90秒の音声のmel-spectrogramと、曲名、アーティスト名、タグを表現に変換する。4層・4ヘッド・幅512のTransformerで協調信号を加え、256次元にまとめる。学習にはInfoNCEと、元のコンテンツ表現に近づける損失（重み0.1）を使う。残差K-meansの3段×32,000コードでSIDを作る。

配信用のencoderは履歴の表現Kを一度だけ計算する。2層のcausal decoderがSIDのトークンを3つ生成し、trieを使って無効な先頭部分が選ばれないようにする。一つのSIDが複数の曲に対応する場合は、その全曲を候補に戻す。Ranking Moduleは4層のcross-attentionを持ち、曲のID、SIDの各段、先頭部分のn-gramを使って候補にスコアを付ける。

履歴表現は共通だが、生成と順位付けには別々の出力部（head）を使う。

<figure class="teaching batch21"><h3>8,192件の履歴を使い、直近2,048件だけを深く処理する</h3><div class="b21-history"><div class="old">過去6,144件<br>長期ブロック O</div><div class="recent">直近2,048件<br>直近ブロック R</div><div class="bridge">① O ⇄ R：両方向のcross-attention</div><div class="bridge">② 全8,192件：self-attentionを1層</div><div class="old">X<sub>O</sub>を保持</div><div class="recent deep">③ 直近だけ7層<br>H<sub>R</sub></div><div class="bridge">④ K = [X<sub>O</sub>; H<sub>R</sub>] → decoder と Ranking Module</div></div><figcaption>原典 Fig. 3.2・§3.3。古い履歴も残すが、追加の層で処理するのは直近の履歴だけだ。</figcaption></figure>

### デコーダーが生成した候補と、実際に表示された候補で教師の採点を学ぶ

教師モデルは10層のcausal履歴encoderと、候補を採点する6層のモデルを持つ。まず次の曲の予測で事前学習し、like > play > skip > dislikeで隣り合う行動のペアをロジスティック損失で学習する。補助headにはBCEを使う。最終的な配信では教師モデルを動かさない。

配信用モデルの損失には、次のトークンを予測する損失（NTP）を使う。そこに、教師との採点差の平均絶対誤差（MAE）を加える。生成した候補と実際に表示された候補の二種類をまとめて平均するのではなく、別々にMAEを求めて足す。訓練時の生成で使うビーム幅は32、評価と配信では1,024。教師がその時点のデコーダーで生成した候補にスコアを付けるため、デコーダーが変わったときの候補分布のずれを抑えやすい。

イベントが起きてから配信のモデル重みが更新されるまでは中央値45分、p99で60分。これには、イベントをセッションにひも付ける15分と、チェックポイントを配布する10分を含む。教師モデルは24時間ごとに更新する。GPUではTriton Inference Server、形状を固定したCUDA graph、torch.compile、bfloat16に加え、ビーム検索用のtop-kと短いKV用のカーネルを使う。

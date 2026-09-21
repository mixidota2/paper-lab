### SIDを提案し、曲に戻してから採点する
固定Qwen2.5-Omniが先頭90秒の音声mel-spectrogramと曲名・artist・tagをencodeする。4層・4 head・幅512のTransformerで協調信号を加え、256次元へpoolingする。InfoNCEと元content表現へのalignment（重み0.1）を使う。残差K-meansの3段×32,000コードでSIDを作る。

配信encoderのmemory Kは一度だけ計算する。2層のcausal decoderが3つのSID tokenを生成し、trieで無効prefixを遮断する。同じSIDに複数曲が入る場合は全曲へ展開し、4層のcross-attentionを持つRanking Moduleがitem ID、SID各段、prefix n-gramを使って採点する。

共有表現でも、生成と順位のheadは別である。

<figure class="teaching batch21"><h3>8,192件を見せるが、深く処理するのは直近2,048件</h3><div class="b21-history"><div class="old">過去6,144件<br>長期block O</div><div class="recent">直近2,048件<br>recent block R</div><div class="bridge">① O ⇄ R：両方向のcross-attention</div><div class="bridge">② 全8,192件：self-attentionを1層</div><div class="old">X<sub>O</sub>を保持</div><div class="recent deep">③ recentだけ7層<br>H<sub>R</sub></div><div class="bridge">④ K = [X<sub>O</sub>; H<sub>R</sub>] → decoder と Ranking Module</div></div><figcaption>原典 Fig. 3.2・§3.3。長期履歴を捨てる圧縮ではなく、処理の深さを配分する。</figcaption></figure>

### teacherが知る順序を、今のdecoderが出す候補へ移す
teacherは10層causal履歴encoderと6層candidate scorerを持つ。まずnext-item predictionで事前学習し、like > play > skip > dislikeの隣接pairをlogistic lossで学習する。補助headはBCE。最終配信にはteacherを置かない。

studentの損失は NTP + rollout候補の平均MAE + impression候補の平均MAE。候補数を全部まとめて平均する式ではない。訓練rollout beamは32、評価・配信beamは1,024。教師の採点は現在のdecoder候補へ追従するため、生成器が変わったときの分布差を埋めやすい。

イベントから配信重み更新までは中央値45分、p99で60分。15分のsession attributionと10分のcheckpoint配布を含む。teacherのrefreshは24時間ごと。GPUではTriton Inference Server、固定shapeのCUDA graph、torch.compile、bfloat16、beam向けtop-kと短いKV用kernelを使う。

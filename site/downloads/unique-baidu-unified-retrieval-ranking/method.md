### EQNは意味だけでcodeを作らない

End-to-End Quantization Networkはitem ID、category、publisher、titleなどと行動feedbackを使う。DSSM形式のtask別user towerと共有item towerを内積で学習し、正規化したitem vectorをflat codeへ割り当てる。codeはEMAで更新し、未使用codeは維持する。Eq. 11の使用率補正はcode利用の偏りを抑える追加策である。

### UIGNとTDNはtargetを早い段階で交差させる

User Interest Generation Networkのprefixはprofile、短期・中期・interest履歴を連結する。Target-Code-Aware Discriminative Networkではcode targetとitem targetがprefixを参照する。code logitはuser–codeの交差表現をMLPへ入れて得る。単独user embeddingとcode embeddingの類似度だけではない。

公開benchmarkのTransformerは3層、4 head、hidden 512、dropoutなし。item/user embedding 256、code embedding 64、codebook 1,024。最大501 tokenはprofile 1、短期100、中期200、interest 200。productionの16,384 codeと混同しない。lossはbinary feedbackの重み付きBCE、durationのMSE、codeのcross entropy、DSSM教師、量子化正則化を合わせる。

### 共有forwardと実際の配信順序は別に読む

学習の共有計算graphはcodeとitemの教師をつなぐ。配信はcode予測→index展開→内積による粗ranking→TDNによる精rankingという順序を持つ。N=100 codeから数十万候補を取り、粗rankingでtop 10k、codeごとの精rankingでM=30を後続処理へ返す。N=200は約2倍の費用に対して多様性の追加利得が小さく、M=10はrecallを損なうという記述がある。

item embeddingは毎時同期、新規itemは初回impressionから5分以内にtraining streamへ入り1時間以内に量子化。昼15秒・夜30秒のcacheでhit率37%・60%。codeの鮮度、モデルversion、cache条件まで含めて89 msを読む。

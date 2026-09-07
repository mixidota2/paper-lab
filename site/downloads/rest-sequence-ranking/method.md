ReSTは **LLaMA型のcausal Transformer + SwiGLU** を推薦履歴向けに改めたモデル。重いsequence encoder Tで履歴を1回計算し、軽いcross decoder Cで候補ごとに読む。CはTの出力HをそのままKeyとValueに使い、候補側でのK/V射影を省く。

TではDual-Gated AttentionがValueと集約後の出力を別々に調整する。RoPEで行動の順序、RoTEで実時間の間隔を扱い、SRNで残差の大きさと正規化位置を制御する。Cは[CLS]・context・user・adというQueryの種類ごとにパラメータを持つ。

学習には主CVR損失に加え、系列だけからCVRを予測する補助BCEと、系列・非系列表現の整合損失を使う。強い非系列特徴だけで正解できると、履歴側が十分に学習されないという問題に対処する。補助headは推論時には外す。

[一次資料：方法と実験条件](https://arxiv.org/html/2609.01240)

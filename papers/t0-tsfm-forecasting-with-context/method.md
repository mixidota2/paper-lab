### alphaの24層は「時間2、変数1」を繰り返す

patchは32時点。t0-alphaはhidden 512、8 head、時間attention 16層と変数attention 8層を持ち、RMSNorm・SwiGLU・QK normを使う。target yと過去変数xの時間方向はcausal、既知未来zは1:T+Hを双方向に読む。変数方向ではy/xがzを読める一方、zはy/xを読まない。逆参照を許すと、zの時間attentionを経由して未来targetが過去へ戻る。

### 正規化にもcutoffを守らせる

y/xは時点ごとのcausal mean/stdで標準化してarcsinhを取る。未来targetの教師はcutoff T時点の統計で固定する。zだけは既知なので全1:T+Hから統計を取れる。欠測はmaskし、統計とlossから外す。static covariateやtext metadataを直接読む機能は本報告の対象外。

alphaのnative分位点は0.1/0.25/0.5/0.75/0.9。最小分位点を直接予測し、残りはsoftplusで正の差分を足す。weighted pinball lossの重みは0.175/0.2/0.25/0.2/0.175。betaは21分位点、0.01–0.99であり仕様が違う。

### 情報の価値とforecastの価値を分ける

同じcheckpointの入切比較はcovariate経路の寄与を捉えるが、その予定が正確か、欠品した売上が需要を表すかは別の問題。さらに出力は各時点のmarginal quantileで、時間・商品間のjoint distributionは持たない。補充費用を計算するには追加の意思決定検証が要る。

本文のalpha通常推論はnative範囲外のquantileを端点に留め、IQF tail外挿を別途評価する。確認時の公式READMEは外挿対応を説明しているので、論文v1と現行APIを同一仕様と決めつけない。

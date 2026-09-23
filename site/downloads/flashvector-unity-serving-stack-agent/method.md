### 計測器を層に合わせる

GPUにはNsight Systems / Compute、serverとfeature処理にはeBPF由来のPython/C++ profileを使う。Diagnoseは時間占有率と期待改善をもとに候補を選ぶ。1 iterationで1層をsampleし、全層を同時に変更しない。Refineはloop終了後で、採択・棄却した知見を更新する。

### 正しさ、noise、全体性能は別のgate

演算順序と精度を維持するrewriteは出力のelement-wise完全一致。浮動小数点の再順序化では、本文はend-to-endの絶対偏差10⁻³と、それを超える要素が最大0.1%という許容を記述し、FP32 servingでは10⁻⁴とする。per-kernelのboundは別にFP32 10⁻³、FP16 10⁻²。non-finiteは失敗。意図的近似はbusiness metric、設定変更は固定SLOのshadow canaryで検証する。本Labはこの数値許容を簡略な一致flagへ置き換える。

無変更のbaseline反復からend-to-end noise floor ±6%を推定。2–6%の改善は最大8倍標本で再測定し、約2.1%までfloorを縮める。正しさに合格しても、そのまま採択しない。全体負荷試験でlatencyとthroughputを再確認する。

### 30倍の局所改善を2倍の全体改善へ混ぜない

Tritonの入力変換をC++化する事例、attentionを融合する事例、embedding bagをcompilerに見えるprimitiveへ分解する事例、featureのzero-copyや一括tensor割当はそれぞれ別の変更。Pythonの関数を速くした倍率を、広告配信全体の倍率へ適用できない。

§5.4の設定探索は現在instance数とdynamic batch sizeの2軸で、queue policyはSLOから導く。production requestを隔離nodeでreplayし、二段モデルはpreprocessor出力を先に収集する。reviewed PRとcanaryがある点も、無審査で本番を自由に書き換えるagent像とは異なる。

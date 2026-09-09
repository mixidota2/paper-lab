### WithinもCrossも、同じ4ハーネスの軌跡を読む
Aider、OpenHands、Qwen Code、SWE-agentでSWE-Gymの軌跡を集める。同一のQwen3-8Bの教師あり学習後checkpointから出発し、固定manifest、token、reward、loss mask、更新予算をそろえて再生する。主要RL群は183課題・5,543episode、81,216recordを共有し、実現したoptimizer stepは81,200（付録G、表7–8）。

### 違うのは平均と標準偏差を計算する範囲
たとえば同じ課題の8軌跡を、Aiderの4件とSWE-agentの4件に分けるか、8件で一群にするかを考える。軌跡eの課題をx、ハーネスをh、成功報酬をrとする。Withinは `A_e = (r_e − mean(r|x,h))/(std(r|x,h)+ε)`。Crossは `A_e = (r_e − mean(r|x))/(std(r|x)+ε)` で、同じ課題の別ハーネスまでまとめる。

このAがGRPOの方策確率比に掛かる。全成功または全失敗の群は分散がゼロなので、Withinでは更新信号が消える。Crossなら別ハーネスとの成功率差が残りうる。これは推論能力の差だけでなく、ツール形式との相性でも生まれる。二値報酬では混合群内の成功は正、失敗は負になる。群を変えて常に符号が逆転するのではなく、ゼロだった信号が正または負になるケースが重要だ。

### 評価には学習時のフィードバックを使わない
SWE-bench Verifiedの500課題を、4つのsourceハーネスと学習に出さない最小weak-ReActハーネスで実行する。sealed oracleはepisodeごとの隔離環境でpatchを再実行し、モデルに見せたfeedback testと異なるhidden testで判定する。inline判定との食い違いが2.58%あり、すべて楽観方向だったため、論文の数字はoracle側だけで集計する（付録L）。

[一次資料：arXiv v1 本文](https://arxiv.org/pdf/2609.04518v1)

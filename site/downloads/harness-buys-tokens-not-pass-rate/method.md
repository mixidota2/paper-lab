モデルは固定する。比較モデルはQwen3.6-35B-A3B、Qwen3.8-27B、DeepSeek-V4-Flash、GLM-5.3-Flash、HY4-Preview。Claude Opus 5はClaude Code内だけの参照で、pool447の比較は2つのQwenに限られる。

同じ課題でAだけ成功した件数をb、Bだけをcとすると、`Δ=(b−c)/n`、不一致率は`q=(b+c)/n`。得点差と、課題の成否が入れ替わる割合は別の量である。McNemarの両側正確検定を使い、対応差の95% Newcombe区間を示す。等価性はTOST、許容幅±5ポイント、90%区間で判定する。

検出力は`M∼Binomial(n,q)`、`B|M∼Binomial(M,(1+Δ/q)/2)`を積分する。不一致件数Mを丸めて固定しない。帰無仮説ではB|Mの成功確率は1/2で、両側p≤0.05となる確率が検出力である。

費用は別に測る。token費用の理解には`Iₖ ≈ P + U + gk`、`ΣIₖ = N(P+U)+gN(N−1)/2`を使う。Pはharnessの定型入力、Uは課題文、gは履歴の増加、Nはstep数。請求はcache hit、miss、出力の単価を分けて足す。下の計算機は入力のみの近似であり、圧縮時点を動かす操作も説明用である。

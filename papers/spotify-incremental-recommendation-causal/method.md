### 共有表現へ二つの観測を流す

Deep Twin Network は既存の multi-task shared-trunk model に holdback head を加え、各群の binary cross-entropy を群内平均して足す（Fig. 3、Eq. 4）。

| 更新する部分 | 学習データ |
| --- | --- |
| treated head | 推薦ありの群 D₁ |
| holdback head | 推薦を止めた群 D₀ |
| shared trunk | 両群 |

割当確率は既知。propensity head は付けない。

### 二つの条件を両方満たす組へ表示する

Eq. 5:

```text
π(x) = 1[p̂₁(x) ≥ θ₁] · 1[p̂₀(x) ≤ θ₀]
```

θ₀を上げるほど表示条件は緩み、θ₀=1で単一閾値へ戻る。原文 §4.2 の説明文には、この方向を逆に述べる箇所があるため、本 Lab の図と実験は式の不等号に従う。

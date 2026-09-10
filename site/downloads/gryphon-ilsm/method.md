### 生成は候補を提案し、ILSM が曲を選ぶ
ユーザー履歴を双方向 Transformer で一度読み、状態列 Eᵤ を decoder と ILSM が共有する。SID σ=(s₁,…,sL) の確率と対数スコアは次の関係にある。

```text
pθ(σ|u) = ∏ᵦ pθ(sᵦ | u, s<ᵦ)
ℓθ(σ|u) = Σᵦ log pθ(sᵦ | u, s<ᵦ)
Cσ = {i : Φ(i)=σ}       Iᵤ = ∪σ∈beam Cσ
```

Cσ は衝突する曲の集合。Cσ 内は全曲が同点になる。beam 内の SID を曲へ展開した Iᵤ に対して、曲の表現 eᵢ をクエリーとして履歴を読む cross-attention と MLP を適用する。

```text
eᵢ = Titem(Φ(i), hᵢ)
rφ(u,i) = fφ(Eᵤ, eᵢ)
TopN(u) = TopNᵢ∈Iᵤ rφ(u,i)
```

一般形の hᵢ は曲 ID・属性・内容を含められるが、報告実験の ILSM は曲 ID だけを使う。追加特徴による優位を避ける比較である。Gryphon は encoder 7層、decoder 2層、ILSM 1層。Vanilla GR の decoder 3層のうち1層を ILSM に置き換え、パラメーター数と推論時間の差を1%未満と報告する。

### 次の曲を当てる損失を、二つの経路で学ぶ
生成側は正解 SID の負の対数尤度 Lgen を最小化する。ILSM は in-batch の負例集合 B⁻ を使い、サンプリング確率 Qᵢ を補正した sampled softmax で次の曲を学習する。

```text
zᵢ = rφ(u,i)/τ − log Qᵢ
LNIP = −log [ exp(zᵢ₊) / Σⱼ∈{i₊}∪B⁻ exp(zⱼ) ]
L = Lgen + λ LNIP                 （報告実験は λ=1）
```

τ は温度、Qᵢ は曲が負例として現れる頻度に対応する確率。共有 encoder は両方の損失を受ける。推薦後の多目的なユーザー価値を直接学んだ実験ではない。[一次資料：§2–3、§4.1.3](https://arxiv.org/html/2606.08604)。

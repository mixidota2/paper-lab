### 履歴を一度読み、生成と採点が同じ状態列を使う
Eᵤ=Encodehist(Hᵤ) は履歴を読んだ状態列。双方向 encoder 7層、decoder 2層、Ranking Module 1層、隠れ幅1024、全体0.5Bパラメーターを使う。学生の履歴は最大2048イベント、教師は最大8000イベント。教師の重い履歴計算は配信経路に入らない。

decoder はカタログ trie に制約した beam search で有効な SID を生成する。SID は3 codebook、各32000要素。配信時は1024 SID を曲へ展開し、最大1200曲に抑える。上限を超える場合は低尤度 SID とその衝突集合をまとめて外す。したがって最終採点の前にも候補選別の影響が残る。

```text
pθ(σ|u) = ∏ᵦ pθ(sᵦ | s<ᵦ, Eᵤ)
Iᵤ = ∪σ∈retained beam { i : Φ(i)=σ }
eᵢ = Encodeitem(item ID, SID prefix n-grams)
ranking heads = RankingModule(Eᵤ, eᵢ)
```

曲表現は曲 ID と SID 接頭辞の n-gram を multi-hash embedding で表す。候補を query にして共有履歴を読み、タスク別スコアを出す。最終順位は教師と同じ固定の組み合わせを使うが、組み合わせの具体的な重みは確認した本文にない。SID の尤度は候補の採否に使い、最終順位は曲単位で決める。

### Rollout Distillation は二つの平均誤差を足す
Gᵤ は現在の decoder を各 training step で走らせた候補、Mᵤ は同じ request の表示ログ。両方を同じ教師が採点する。r̂ᵗ は学生、rT,ᵗ は教師、T は順位付けタスクの集合である。

```text
Lroll = (1/|T|) Σₜ (1/|Gᵤ|) Σᵢ∈Gᵤ |r̂ᵗᵤᵢ − rT,ᵗᵤᵢ|
Limpr = (1/|T|) Σₜ (1/|Mᵤ|) Σᵢ∈Mᵤ |r̂ᵗᵤᵢ − rT,ᵗᵤᵢ|
L = LNTP + Lroll + Limpr
```

LNTP は正の表示曲の SID を学ぶ next-token prediction 損失。順位の教師信号は Teacher Ranker のスコアだけであり、表示ログのラベルを Ranking Module に直接与える方式ではない。異なる候補の90%超が rollout 由来でも、損失は候補源ごとに正規化して係数1で足す。損失は90対10ではない。

NTP は decoder と encoder を、蒸留は Ranking Module と encoder を更新する。beam search には勾配を流さない。policy gradient も使わない。[一次資料：§3、Appendix A](https://arxiv.org/html/2608.06213)。

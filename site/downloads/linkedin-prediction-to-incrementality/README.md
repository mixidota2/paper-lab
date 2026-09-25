# LinkedIn：反応予測から増分の配分へ

## Overview — 8週間でLTV +7.20%

LinkedInは、送った場合と送らなかった場合の成果の差を推定し、探索と全体制約を含む配分へつなぐ。Feedのマーケティング流量で実施した8週間のA/Bでは、長期価値（LTV）が+7.20%だった。p=0.041、95%信頼区間は[0.31%, 14.09%]。これは配信方策全体の著者報告で、Transformer単体の効果ではない。

## Problem — 自然に起こる成果へ予算を使わない

反応確率の高い会員は、送信しなくても行動するかもしれない。限られた予算をそこへ使うと、送信によって行動が変わる会員へ届かない。さらに、各キャンペーンが個別に最適化すると、全体予算や会員ごとの送信上限を超えうる。

## Core Idea — 著者の主張と本Labの解釈

著者の主張：Transformerで接触履歴を読むDragonNet、最終層の線形化Laplace近似によるBayesian neural-bandit、双対分解による大規模配分を一つの増分目的へそろえる。負の増分や実行可能な正の選択肢がない場合は送信を保留する。

本Labの解釈：[Netflixの反実仮想観測](netflix-counterfactual-observability.html)、[Spotifyの二閾値](spotify-incremental-recommendation-causal.html)、[PinterestのCG gating](pinterest-causal-retrieval-shopping.html)に続く読み筋として、全体資源を配る第4の層と捉える。この比較は本Labの整理で、四社を同じ実験で評価した結果ではない。

## Why It Might Work — 推論の前提を残す

本Labの解釈。反実仮想との差で採点すれば、自然に起こる成果へ予算を使う問題を抑えられる。探索は実行可能な行動の観測機会を残し、配分は共通の制約を守る。ただし、未観測交絡がないこと、処置の重なりが十分あることなどの識別条件は、DragonNetを使うだけでは満たせない。

## Evidence — 方策全体のA/Bを読む

著者報告：§5.4–5.5では会員を50/50に無作為割付し、8週間比較した。対照は反応確率に基づく候補抽出と順位付けの二段構成。処置はマーケターの対象条件を残し、二つのスコア層を因果スコアと制約付き配分へ置換した。LTV +7.20%、p=0.041、95% CI [0.31%, 14.09%]。同じ本番方策の構成要素を個別に外したオンライン効果は報告していない。

初期実験では処置群の配信量が不足したため、実配信と費用のフィードバックを加えた。最終比較はBAUの配信量・費用の範囲に合わせる設計である。公開banditデータによるオフラインsimulationとFig. 3の5回反復ablationは、LinkedInのA/Bとは別の証拠である。

## Executable Understanding — 4人の配分を全探索する

`UV_CACHE_DIR=/tmp/uv-cache uv run papers/linkedin-prediction-to-incrementality/run.py`。4人・1施策の人工例で、送信時成果の最大化と増分成果の最大化を、同じ予算制約で比較する。各人の未送信・送信時の期待値は既知として与える。16通りを列挙するため、解の確認に学習や外部solverは不要である。

## Results — 予算3で増分0.20と0.50

予算3では、反応最大化はA・B・Dへ送り、増分の合計は0.20。増分最大化はC・Dを選び、0.50となる。予算5でも、増分が負のAには送らず、費用は4で止まる。この例は、反応率の高さと送信の価値が違うことを確かめるために設計した。論文の改善率を再現した値ではない。

## What We Verified — 人工例の配分を確認

Mechanism PARTIAL。人工例の全実行可能解を列挙し、負の増分を持つAを保留すること、容量によって配分が変わることを確認した。この二つの局所条件はCONFIRMED。PDFのFig. 1を目視し、数式と本番実験の記述を本文と照合した。

## What We Did NOT Verify — 学習と本番は未検証

Performance / Scaling / Production applicability NOT TESTED。Transformer-DragonNetの学習、last-layer LLAの曲率推定、Thompson sampling、双対solver、実配信フィードバック、LinkedInのログとA/Bは実行していない。大規模時の99%以上の最適値回復や新商品への汎化も独立検証していない。

## Implementation — 標準ライブラリで実行

`ROWS`が人工的な潜在結果の平均、`allocate()`が全探索、`compute()`が同じ予算での比較とassertionを担当する。Python標準ライブラリだけで動く。乱数を使わず、実行するたびに`results.json`を書き直す。HTMLは`lab.yaml`と文書・結果から生成する。

## Original Paper / Official Code Mapping

[原論文](https://arxiv.org/abs/2608.10182)の対応箇所は[mapping.md](mapping.md)、詳細は[method.md](method.md)を参照。確認した提供論文には公式実装へのリンクが見当たらない。

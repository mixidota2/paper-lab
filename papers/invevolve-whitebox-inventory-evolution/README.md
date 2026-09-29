# InvEvolve：発注コードを進化させ、配備前に改善の下限を確認する

## Overview — 白箱の発注規則と認証を組み合わせる

InvEvolveは、LLMが読める発注コードを生成し、同じ需要履歴で比較してから配備する仕組みである。著者報告では合成OODの25/30件、Dunnhumby Complete Journey（CJ）の20/30件で最良の古典方策を上回る。CJの費用削減9.2%は**勝った20件に限る平均**で、全30件の平均ではない。

採用と配備を分ける。候補を残す判定は慎重に、通過候補の選択は楽観的に行う。ただし将来の安全性は、需要変化を覆う予算や信頼区間の前提に依存する。本Labは発注式と認証の保守性を確かめ、性能を追試しない。

## Problem — 履歴で良かったコードを将来へ移せるか

対象は需要を満たせない分が逸失する在庫管理。古典方策は読みやすいが、販促や季節情報を使う形を人が設計する必要がある。LLMに自由なコード探索を任せても、履歴への過適合と需要シフトは残る。

## Core Idea — 著者の主張とLabの解釈

著者は、GRPOで学習したGLM-4.7-Flash（30B MoE）によるLGPS（LLM-guided policy search）を提案する。候補コードを生成し、共通の需要経路でreplay評価し、改善の信頼下限LCBで候補を絞る。通過候補から信頼上限UCBが最大の方策を配備し、候補がなければ参照方策へ戻る。探索中のchampion昇格には、参照に対する安全性に加え、現championへの改善条件も置く。

Labの解釈では、これは「方策そのものをコード空間で改善する」セルに入る。[SabreAgent](../sabreagent-design-time-inventory/README.md)のセルは「設計時に季節事前分布を構成し、凍結したORルールを実行する」。InvEvolveは窓ごとに方策探索を更新するが、各発注でLLMへ数量を直接尋ねる設計とは区別する。InventoryBenchとの直接対決ではない。

## Why It Might Work — 生成の自由度と採用の慎重さを分ける

解釈：候補を実行可能な規則にすれば、既存方策と同じ経路で費用差を測れる。改善量を Z=C_ref−C_candidate と置くので、正なら改善である。Eq. 7の半径とEq. 8の信頼限界は次の形になる。

```text
rad = B sqrt(2 log(2N/δ) / m)
LCB = mean(Z) − rad; UCB = mean(Z) + rad
安全候補: LCB ≥ ξ; 配備: 安全候補中の最大UCB
```

Bは改善量の絶対値の上限、Nは比較数の上限、mはreplay経路数、δは期間ごとの失敗確率予算。ξはreplayと配備分布の最悪差を覆う予算である。多重比較も効く。候補が多ければ半径は大きくなる。付録Eの実用ξ校正と付録Fの小標本blockwise t半径は、理論式を無条件に満たす証明とは分けて読む。

## Evidence — 30件の外挿と96条件の方策比較は別の実験

| 著者報告 | 比較 | 成績 |
| --- | --- | --- |
| 合成30件、Table 2 | 最良古典方策に対する勝率 | base GLM 13/30、InvEvolve 25/30 |
| CJ 30件、Table 3 | 最良古典方策に対する勝率 | A3C 11/30、E2E 16/30、InvEvolve 20/30 |
| 定常96条件、Table 6 | CBSに対する勝／同等／負 | Tilted-CBS 18/74/4、Tilted-PIC 41/47/8 |

合成は100日で設計、将来30日で評価。訓練に用いた10 workspaceと商品が重ならず、10業界中5業界は未学習。CJは365日から次の30日を評価し、販売を潜在需要へ復元したbenchmarkである。復元品質が主張の中心ではなく、実店舗の因果的な費用改善を示す試験でもない。

96条件は6需要分布×4リードタイム×4欠品費用比。±2%以内を同等とするため、beat-or-tie 95.8%（Tilted-CBS）と91.7%（Tilted-PIC）は厳密な勝率ではない。平均費用変化は−0.60%と−1.52%、最悪は+5.4%と+4.2%。全条件の改善保証ではない。

## Executable Understanding — 不足に応じて発注上限を傾ける

```text
Δ = max(0, S − IP)
CBS:        q = min(Δ, r)
Tilted-CBS: q = min(Δ, r_base + αΔ)
Tilted-PIC: q = max(0, min(round(Kp Δ), r_base + αΔ))
```

IPは手元在庫と輸送中在庫を合わせた在庫ポジション。αは不足が大きいとき上限を緩め、Kpは不足への反応を調整する。α=0のTilted-CBSはCBSに戻る。整数不足でKp=1ならTilted-PICはTilted-CBSに一致する。対話図ではこれらの係数を変え、同じ不足に対する発注量を比較する。

## Results — 人工需要では改善しても認証を通過しない

seed=930、256経路×60日、需要は0〜10の離散一様分布。L=3、S=24、r=4、保管費1、逸失費9を固定した。平均費用はCBS 12.402、Tilted-CBS 9.501、Tilted-PIC 10.037。係数は固定した。探索は省いた。

一方、費用上限114から得る半径は21.093。改善のLCBは−18.191と−18.728になり、ξ=0でも安全候補は空となる。平均費用の改善と統計的な採用条件が別物であることを確認できる。

## What We Verified — 局所式と認証の保守性を確認した

MechanismはPARTIAL。α=0でのCBSへの帰着、整数不足でのKp=1の一致、費用の有界性はCONFIRMED。共通需要経路での改善平均、LCB/UCBの計算を実行した。候補認証の成功はNOT OBSERVED。

## What We Did NOT Verify — LLM探索と性能再現は未実行

Performance / Scaling / Production applicabilityはNOT TESTED。GRPO学習、コード生成、champion更新、需要シフト予算の校正、公式の小標本半径、CJ復元、96条件の再最適化は実行していない。人工実験の費用差から、論文の勝率や将来配備の安全性は推論しない。

## Implementation — 標準ライブラリだけで再実行する

`UV_CACHE_DIR=/tmp/uv-cache uv run --no-project papers/invevolve-whitebox-inventory-evolution/run.py`

`run.py`は到着→発注判断→需要消化の順に在庫を進める。需要経路は全方策で共通。`results.json`に人工結果と著者集計を分けて保存し、図はその値から生成する。発注の丸めには非負数の四捨五入を使う。連続量での丸め境界は原論文の実装を確認していない。

## Original Paper / Official Code Mapping — 本文と付録に戻れるようにする

[原論文 v4](https://arxiv.org/pdf/2605.00369v4)の§2・Fig. 2が認証、§4が学習、§5.1–5.3が評価、§5.3.2・Fig. 5が発見方策。対応と省略範囲は[mapping.md](mapping.md)に記す。次の検証対象は、実需要でのξ校正がどれほど保守的か、そして採用できる候補が残るかである。

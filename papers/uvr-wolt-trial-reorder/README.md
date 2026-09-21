# Balancing Trial and Reorder: A Hybrid Sequential Transformer–GBDT Ranker for On-Demand Delivery

UVRは双方向TransformerのlogitをCatBoostへ渡す。V1はtrial +5.5%、CVR +0.16%。V2はtrialを伸ばす一方、reorder MRRが6カ国中5カ国で後退した。

優先度: Worth Reading。確認日: 2026-09-21。

## 実行

```sh
uv run papers/uvr-wolt-trial-reorder/run.py
uv run paper-lab build
```

## Overview

WoltのUniversal Venue Ranker（UVR）は、購入履歴を読む双方向Transformerのlogitを、CatBoostの特徴量に加える。V1の2週間・50:50 A/BではMerchant Trial Rate +5.5%、Global CVR +0.16%（p=0.017）。V2でtrialをさらに重視すると、再注文のオフラインMRRは6カ国中5カ国で旧productionを下回った。

## Problem

配達できない店舗は、好みに合っていても候補にできない。営業時間、距離、配達員、混雑で候補集合はrequestごとに変わる。また、いつもの店から買うreorderと、新しい店を試すtrialでは必要な順位が違う。平均MRRだけを最適化すると、利用頻度の高い再注文が学習を支配しやすい。

## Core Idea

履歴classifierとcontext・contentを扱うGBDTを組み合わせ、trial-aware weightingで運用点を選ぶ。V3で飲食店と小売の履歴を共有し、4つの旧rankerを統合した。

解釈: 国別学習と領域間共有を分けて読む。sequenceモデル対GBDTという二者択一より、どの信号をどこで学習し、何をガードレールにするかが実務上の焦点になる。

## モデル / 手法

[method.md](method.md) の図と数式を読む。

## Why It Might Work

履歴の長期パターンをTransformerで圧縮し、配送料や距離の非線形な条件を木で扱えば、役割を分けて運用できる。[OTTOのGBDT対DNN](otto-gbdt-vs-dnn-ltr.html)の「どちらを選ぶか」に対し、ここでは組み合わせ方が問いになる。[REST](rest-sequence-ranking.html)とも、sequence表現の計算場所と最終rankerの責任を比べたい。

## Evidence

一次資料の著者報告。

[原典 Tables 3–5・§6](https://arxiv.org/html/2609.16407v1) の著者報告。全テストはuser-level 50:50。V1/V2は上位10カ国で2週間、V3は全稼働国で3週間。

| 版・control | Merchant Trial Rate | Global CVR |
| --- | ---: | ---: |
| V1 vs FPR+SPR/CSR | +5.5% | +0.16%, p=0.017 |
| V2 vs V1 | +0.45% | −0.05%, p=0.398 |
| V3 vs V2+RR | 小売 +1.31% | +0.04%, p=0.457 |

trialの差はα=0.05で有意。V2/V3のCVRは有意差を確認していない。「変化しないことを証明した」とは言えない。V3のads revenueは−0.43%で、事業指標の交換条件も残る。

V2の旧production比trial MRRは+12.5%〜+30.3%。reorderはFINのみ+6.7%、他は−1.4%〜−27.3%。同じ表のV1 trialは+7.5%〜+19.8%なので、12–30%をV1へ帰属させない。seed間のばらつきも平均upliftの約10–30%ある。運用点はreorder回帰−15%以内を目指すが、DEUでは条件を満たす点がなかった。

日次学習はFlyte/Kubernetes、推論はCPU、feature取得等を含むp99は約60ms。classifierは学習時に見た店舗だけを識別するため、新店追加も日次更新の理由になる。

## Executable Understanding

同じ合成logit・距離特徴を使い、pairwise logistic lossのtrial/reorder重み比だけを1、2、3、5へ変える。未使用400sessionで両群MRRを分けて測る。全店舗で最高logitの店が配達不可なら除外されることと、smoothed targetの総和も検査する。これは学習できる線形代理で、CatBoostやTransformerの再実装ではない。

## Results

以下はこのLabの実行結果。上のEvidenceに載せた著者報告のA/Bとは、データも評価対象も異なる。

## What We Verified

Mechanism PARTIAL。固定した2候補の曖昧な意図分布で、重み比を上げるとtrial MRRは0.5から1.0、reorder MRRは1.0から0.5へ動いた。重みで目的を変える操作の確認であり、trial性能向上の一般的な証拠ではない。

## What We Did NOT Verify

Performance / Scaling / Production applicabilityはNOT TESTED。実CatBoost、双方向Transformer、国別データ、配信60ms、A/Bを再現していない。原典も、同条件でlogitを抜くablationと領域別Transformerを用いた対照を未実施としており、V3の改善をcross-domain transferだけに帰属できない。

## Implementation

`fit()`はsession重み付きpairwise線形学習、`metrics()`はtrial/reorder別MRR、`smooth_target()`と`eligible_scores()`は学習labelと配達可能集合の境界。条件を固定した操作実験である。

Python標準ライブラリだけで実行する。乱数を使う実験はseedを固定し、結果をコードと同じ場所に保存する。

## Original Paper / Official Code Mapping

[mapping.md](mapping.md)

# LIGE-GR: A Smooth Leap from Ranking to Generative Recommendation in the LLM Era

LIGE-GRは既存候補poolの中で列を生成する追加型の設計。beam 1の7日A/BでReels視聴時間+1.14%、FB+0.72%。FB視聴回数−0.52%も併記する。

優先度: Must Read。確認日: 2026-09-21。

## 実行

```sh
uv run papers/lige-gr-meta-listwise/run.py
uv run paper-lab build
```

## Overview

成熟したpointwise rankerを保ったまま、選んだ動画同士の関係を順位に反映する。LIGE-GRの価値は、既存の予測・業務制約・運用責任を使い続けられる移行経路にある。Instagram ReelsとFacebook Videoで7日間のA/Bを実施し、Time spentは+1.14%と+0.72%。ただし、これはCAを使うbeam 1の基本構成である。

## Problem

高得点の動画を独立に並べても、似た話題が連続すれば後続動画の価値は変わる。従来のcontrol layer（CL）は多様性や禁止条件を補うが、予測自体は選択済みの列を見ていない。そこで、数百件の既存候補poolから約10件の列を作る部分を更新する。全カタログからSIDを生成する問題までは解いていない。

## Core Idea

CFの表現をCAが選択済みprefixで更新し、ListVMをPaletteで最大化する。既存CLとCFを保持するため、追加部分を停止して元の順位付けへ戻せる。

解釈: [Sona](sona-yandex-music.html)・[Gryphon-v2](gryphon-v2-cascade.html)のcascade置換とは移行単位が違う。[OGR](ogr-once-generated-ranked.html)・[GenPage](genpage-netflix-homepage.html)のslate統合とも、候補空間と生成責任を分けて比較したい。

## モデル / 手法

[method.md](method.md) の図と数式を読む。

## Why It Might Work

重いCFを各位置で再計算せず、小さいCAに列内の飽和や補完関係だけを担わせるので、既存rankerの精度を捨てずに探索を追加しやすい。継続確率の重み付けは、到達されない後半の価値を過大評価しにくくする。一方、候補poolの外に正解がある場合は回復できず、継続確率の誤差は後半へ累積する。

## Evidence

一次資料の著者報告。

[原典 §4–5・Tables 1–4](https://arxiv.org/html/2609.18148v1) の著者報告。Reelsはcontrol/treatment各1.5%、FBはtreatment約2%と同程度のcontrolで、両方7日間。Time spentの差は両面でp<0.001。

| 指標 | Reels | Facebook Video |
| --- | ---: | ---: |
| Time spent | +1.14% | +0.72% |
| Video views | +2.28% | −0.52% |
| Likes / reactions | +2.65% | +1.59% |
| Sessions | +0.11% | +0.07% |

FBは視聴時間が増えても視聴回数が減る。体験全体の改善を、全指標の一方向の改善と言い換えない。Reelsの構成診断では72時間未満の新しい動画の割合も−0.66%だった。

追加推論資源は基本構成でCF部分の約10%。サービス全体の計算量の10%ではない。Reelsのend-to-end request latencyは約+7%、FBの平均serving latencyは約+2.2%で、定義が違うため直接比較しない。pool削減による60–80%はCA経路のthroughput増加であり、処理時間60–80%削減ではない。beam 6はbeam 1の約2.1倍の追加資源を要し、CF比約20%は導出値である。

Table 3ではCAを共通に、beam 6のみへの変更はTime spent +0.05%。golden + duration-awareのbeam 6は+0.69%だった。各行はbeam 1に対する独立比較で、+1.14%へ単純に足さない。

## Executable Understanding

同じ7候補・3枠・禁止条件でpointwise、CA beam 1、golden beam 6、top-3 pool、時間予算超過を比較する。小さい全順列oracleも計算する。予測値は固定した人工値であり、探索がよい列を見つけてもCAを学習できた証拠にはならない。`uv run papers/lige-gr-meta-listwise/run.py`。

## Results

同じ継続重み付き目的で、pointwiseとCA beam 1はともに14.732（CA単独の順位改善はNOT OBSERVED）。golden beam 6は21.754へ上がるが、全順列oracleの22.512には届かない。top-3 poolもこのbeam設定では21.754のまま、評価回数は72から12へ減る。ただし候補4を除くのでoracleの列は失われる。これは演算回数の比較で、GPU throughputの再現ではない。

## What We Verified

Mechanism PARTIAL。有限候補で重複と禁止遷移を排除し、継続確率に沿って価値を累積した。時間切れ時の列がpointwise baselineと一致することをassertで確認。全順列の最大値と比較できる。候補削減が探索可能な列を狭める様子も記録した。

## What We Did NOT Verify

Performance / Scaling / Production applicabilityはNOT TESTED。CAの学習、実ログでのNE、A/B差、GPU throughput、実時間timeout、鮮度・creator多様性への効果は再現していない。将来価値推定が許容的な上界である保証もなく、有限beamは最適性を保証しない。

## Implementation

`score()`はEq. 9の到達確率積、`future()`はEq. 12/14、`decode()`はAlgorithm 1/2の制約付き拡張と復帰を表す。candidateのgroupによる減点はLab独自のCA代理。実装をPaletteの公式版と呼ばない。

Python標準ライブラリだけで実行する。乱数を使う実験はseedを固定し、結果をコードと同じ場所に保存する。

## Original Paper / Official Code Mapping

[mapping.md](mapping.md)

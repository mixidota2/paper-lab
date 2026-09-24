# Pinterest：shopping 候補生成を呼ぶ価値を測る

## Overview — 発火を選ぶ

Shopping Holdout と offline replay を使い、shopping 候補生成器（CG）の発火閾値を決める。

## Problem — 買物と保存の目的が競合する

一律の発火は買物行動を増やす一方、Pin 保存などを減らす。目的が競合する。

## Core Idea — 学習と配信を分ける

著者は結果予測と DR uplift を共同学習する。本番の主方策は結果確率 μ₁を使う single-value（SV）であり、差分を使う delta policy（DP）は診断に用いる。

## Why It Might Work — 反対の行動もログに残す

解釈: 対象リクエスト内の50:50の無作為割当が、発火と非発火を比べる根拠になる。

## Evidence — 数字の実験条件を分ける

Table 4 の δ=0.0102 はオンライン−64.4%、オフライン−64.6%で、baseline model の SV 方策を比べた値。

Table 5 は Success Curation の量が+0.26%、Closeup の Repins が+1.10%。この群の発火削減は約40%で、最大85%削減は別群の報告となる。

## Executable Understanding — DR と replay を計算する

```sh
uv run papers/pinterest-causal-retrieval-shopping/run.py
```

3種類・600件の合成 Holdout を使い、誤った結果予測に正しい割当確率を組み合わせて Eq. 7 を確認する。

## Results — 補正と閾値の結果

切り詰め前の DR 平均は真の uplift 0.02、0.20、0.05に一致し、δ=0.3の replay 報酬率は真値と同じ0.426667になる。

## What We Verified — 限定した機構

Mechanism PARTIAL。既知の割当確率による補正と、均等割当下の一致抽出を確認済み。

## What We Did NOT Verify — オンライン性能は未検証

Performance / Scaling / Production applicability は NOT TESTED。ニューラル学習、切り詰め、本番 A/B、遅延は再現していない。

## Implementation — 最小の直接計算

dr() は Eq. 7、evaluate() は一致した行の平均を計算する。Algorithm 1 の高速 sweep を省いた O(nk) の実装。

## Original Paper / Official Code Mapping

一次資料の所在と SHA-256 は [mapping.md](mapping.md)、詳細解説と図の定義は [lab.yaml](lab.yaml)、実行値は [results.json](results.json) を参照。

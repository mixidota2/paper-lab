# Spotify：推薦がなくても再生される組を除く

## Overview — 表示を7.1%減らした

Spotify Home の2週間の A/B で、推薦表示は−7.1%、消費は−0.37%で有意差なし（Table 1）。

## Problem — 二つの計測窓が異なる

推薦ありは短い直接反応、holdback は2日間の自然再生を測るため、予測値の差を CATE と解釈できない。

## Core Idea — 主張と解釈

著者は既存の holdback を学習に再利用し、二重閾値で表示を選ぶ。本 Lab では、因果効果の推定器というより、A/B で検証した配信方策と読む。

## Why It Might Work — 自然再生の高い組を外す

解釈: 推薦なしでも再生しそうな組を外せば、表示枠を別の候補へ回せる。

## Evidence — 比較対象を固定する

Table 1 の比較は Treatment-Causal 対 Treatment-Model。

| 指標 | 相対差 | 95% CI |
| --- | ---: | --- |
| 表示 | −7.1% | [−7.2%, −6.9%] |
| 消費 | −0.37% | [−0.86%, +0.21%] |

Fig. 4 の校正改善は著者の観測であり、改善理由の独立検証はない。

## Executable Understanding — 閾値を動かす

```sh
uv run papers/spotify-incremental-recommendation-causal/run.py
```

4組の固定データで π=1[p̂₁≥0.4]·1[p̂₀≤θ₀] を計算し、単一閾値と比べる。

## Results — 表示削減にも小さな損失がある

θ₀=0.5では表示が3件から2件、追加再生の期待値が0.82から0.80、全再生の期待値が2.37から2.35へ変わる。

## What We Verified — 方策の境界を確認

Mechanism PARTIAL。単調性、θ₀=1での baseline 一致、異なる窓の引き算による符号反転を確認済み。

## What We Did NOT Verify — 学習と本番は対象外

Performance / Scaling / Production applicability は NOT TESTED。共有 trunk、校正、A/B は再現していない。

## Implementation — 式を基準にする

原文 §4.2 の閾値方向の説明は Eq. 5 と矛盾するため、実験は式に従う。θ₀を上げると表示条件が緩む。

## Original Paper / Official Code Mapping

一次資料の所在と SHA-256 は [mapping.md](mapping.md)、詳細解説と図の定義は [lab.yaml](lab.yaml)、実行値は [results.json](results.json) を参照。

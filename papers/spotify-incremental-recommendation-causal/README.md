# Spotify：推薦がなくても再生される組を除く

## Overview — 表示を7.1%減らした

Spotify Homeの2週間のA/Bでは、推薦表示は−7.1%でした。消費は−0.37%で、統計的に有意な差はありませんでした（Table 1）。

## Problem — 二つの計測窓が異なる

推薦ありの記録は表示直後の短い反応、推薦を出さずに残した比較群（holdback）は2日間の自然再生を測ります。観測する時間が違うので、二つの予測値を引いても、条件付き平均処置効果（CATE）にはなりません。

## Core Idea — 主張と解釈

著者は既存のholdbackの記録を学習に使い、二つの閾値で推薦を表示するか決めます。このLabでは、差を因果効果として推定する手法というより、A/Bで検証した表示ルールと読みます。

## Why It Might Work — 自然再生の高い組を外す

推薦しなくても再生されそうな組を除けば、空いた表示枠を別の候補に回せると考えられます。これはLabでの解釈です。

## Evidence — 比較対象を固定する

Table 1はTreatment-Modelを基準に、Treatment-Causalとの差を示します。

| 指標 | 相対差 | 95% CI |
| --- | ---: | --- |
| 表示 | −7.1% | [−7.2%, −6.9%] |
| 消費 | −0.37% | [−0.86%, +0.21%] |

Fig. 4で校正が改善したのは著者の観測です。なぜ改善したかは独立に検証されていません。

## Executable Understanding — 閾値を動かす

```sh
uv run papers/spotify-incremental-recommendation-causal/run.py
```

4組の固定データに π=1[p̂₁≥0.4]·1[p̂₀≤θ₀] を適用します。二つの条件をともに満たす組を表示し、閾値が一つの場合と比べます。

## Results — 表示を減らしたとき、再生の期待値も少し下がる

θ₀=0.5では、表示が3件から2件に減ります。推薦による追加再生の期待値は0.82から0.80、全再生の期待値は2.37から2.35に下がります。

## What We Verified — 方策の境界を確認

仕組みは一部確認済み（Mechanism PARTIAL）です。閾値の変更に対する単調性、θ₀=1で比較元（baseline）と一致すること、計測窓の異なる値を引くと符号が逆転する例を確認しました。

## What We Did NOT Verify — 学習と本番は対象外

性能、規模を広げたときの挙動、本番適用（Performance / Scaling / Production applicability）は未検証（NOT TESTED）です。共有部分（trunk）の学習、確率の校正、A/Bは再現していません。

## Implementation — 式を基準にする

原文 §4.2 の説明と Eq. 5 では、閾値を動かしたときに表示条件が変わる方向が逆です。この実験は式に従います。θ₀を上げると条件が緩みます。

## Original Paper / Official Code Mapping

一次資料の所在と SHA-256 は [mapping.md](mapping.md)、解説と図の定義は [lab.yaml](lab.yaml)、実行結果は [results.json](results.json) にあります。

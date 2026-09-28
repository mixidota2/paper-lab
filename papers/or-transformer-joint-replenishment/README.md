# OR-Transformer: Scaling Real-Time Decision-Making to 1,000 Items

共同発注の有無と、千商品の数量をどう分けて学習するか

## Overview — 要点

OR-Transformerは商品順に依存しないTransformerと、在庫動態を通る勾配で共同補充を学ぶ。1,024商品で最良の学習比較法より費用が約75%低い。合成環境での結果であり、実店舗の導入効果ではない。

## Problem — 問題設定

複数商品に共通の発注固定費Kがある。注文を開いたら各商品へ数量を配分し、欠品分はbacklogとして繰り越す。評価は相関のある合成Poisson需要、異なる納期と商品別費用を用いる。DingdongやJDの現場データでも、棚割りRCTでもない。

## Core Idea — 著者の主張と解釈

著者の主張：共有固定費を払って注文を開く離散判断Yと、各商品の連続量Qを分ける。Yにはscore gradient、Qには在庫動態を通じたpathwise gradientを使う。

Labの解釈：Transformerだけの効果とは読めない。Transformer-PPOとの比較は数量の勾配推定法、MLPを使うHPOとの比較は商品間の表現を考える材料になる。ただし各要素の寄与を完全に分離した因果推定ではない。

## Why It Might Work — 効くと考えられる理由

解釈：商品を並べ替えても問題は変わらないため、位置IDを使わない共有表現が自然である。数量を変えた影響は将来の在庫費用まで伝わる。その経路を直接微分すれば、数量ごとにサンプル報酬だけから効果を推測する負担を減らせる。

## Evidence — 著者の報告

一次資料[Table D.5・Figures 1.1, 4.1](https://arxiv.org/pdf/2609.01933v2)の著者報告。128個の固定評価episodeを使う。50意思決定の比較では1,024商品の費用がOR-Transformer 0.35M、最良の学習比較法PPO 1.39M。1・4商品ではHPOが最良なので、全規模での優位ではない。

別の8意思決定の比較は、Gurobiに各意思決定6時間まで与える。費用126.61±4.23K対156.58±4.93Kで19.1%減。合計判断時間は0.0432秒対48時間49分で400万倍超の差。学習時間を含む比較ではない。50意思決定・10分制限の表と混ぜない。

## Executable Understanding — 手元で確かめる

`uv run papers/or-transformer-joint-replenishment/run.py` で同じフォルダーのresults.jsonを更新する。Python標準ライブラリだけで動く。

固定重みのスカラーself-attentionで6通りの商品順を試す。2期のbacklog費用では、同じQに対する解析勾配を中央差分と照合し、注文を開くBernoulli変数のscore gradientも厳密な期待費用の微分と比較する。

## Results — 人工例の結果

商品を並べ替えると数量出力だけが同じ順に入れ替わり、global出力は変わらない。Qが0.5、2.5、4.5の場合、数量方向の費用勾配はそれぞれ−8、−3、2。過少在庫では増量が費用を下げ、十分な在庫では保有費用が増える。

## What We Verified — 確認した範囲

CONFIRMED：固定attentionの順序同変性、区分的に滑らかな在庫費用の微分、Bernoulliのscore gradientの恒等式。MechanismはPARTIAL。

## What We Did NOT Verify — 未検証の範囲

Performance / Scaling / Production applicabilityはNOT TESTED。Transformerの学習、PPO/HPOとの訓練比較、1,024商品、Gurobi、実店舗での運用は未検証。屈曲点での微分や長い納期の学習安定性も調べていない。

## Implementation — 実装

attention()はglobal tokenと商品tokenに同じ演算を適用する。cost()は2期の保有費用とbacklog費用、derivative()はそのQ微分。Kは1回だけ課金し、閉じた注文ではQが在庫へ影響しない。

## Original Paper / Official Code Mapping — 原典との対応

[式と図の説明](method.md)、[原典・実装対応表](mapping.md)、[実行結果](results.json)を参照。ページはlab.yamlとこれらのファイルから生成する。

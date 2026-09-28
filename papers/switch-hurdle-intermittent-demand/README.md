# Switch-Hurdle: A MoE Encoder with AR Hurdle Decoder for Intermittent Demand Forecasting

ゼロが続く需要で、発生確率と発生時の量を分けられるか

## Overview — 要点

Switch-HurdleはTop-1 MoE encoderと自己回帰hurdle decoderを組み合わせる。M5のWRMSSEは0.6307。予測精度の結果であり、在庫費用やサービス水準の改善は示していない。

## Problem — 問題設定

ゼロが続き、ときに大口の需要が入る。M5の30,490系列と社内の約40,000系列を使い、56日の文脈から28日先を予測する。平均へ平滑化するだけでは、需要が発生する頻度と発生時の数量を捉えにくい。

## Core Idea — 著者の主張と解釈

著者の主張：学習したrouterが各tokenを1つのexpertへ送り、decoderは需要の発生確率と正の需要量を別々に予測する。正の量にはゼロで切り詰めた負の二項分布を使う。

Labの解釈：ゼロの頻度と発生時の大きさを分ける設計は、間欠需要を読む助けになる。ただしAccuracy Is Not Serviceが問う、精度と在庫サービスのずれを解消した研究とはいえない。

## Why It Might Work — 効くと考えられる理由

解釈：発生の確率p⁺を動かしても、発生時の分布は固定できる。逆に正の需要量を変えてもゼロ確率は変えずに済む。MoEの役割は学習する表現を分けることだが、Zero・Low・Normal・Spikeを手でexpertへ割り当てる仕組みではない。

## Evidence — 著者の報告

一次資料[Table 4・Figures 4–5](https://arxiv.org/pdf/2602.22685v1)の著者報告。M5のWRMSSEはSwitch-Hurdle 0.6307、TSMixer 0.6403、TFT 0.6932、DeepAR 0.7895。すべての指標で最良ではなく、RMSEはPatchTST 2.4562に対して2.4744、MASEはTFT 0.8983に対して0.8992。社内全量のWAPEは53.99%。

Zeroなどの区分は、検証データで学習後のroutingを集計したもの。第0層ではZeroの67.5%がexpert 3、Lowの90.8%とSpikeの94.0%がexpert 1へ入る。これは専門化の観察であり、在庫の意思決定評価ではない。

## Executable Understanding — 手元で確かめる

`uv run papers/switch-hurdle-intermittent-demand/run.py` で同じフォルダーのresults.jsonを更新する。Python標準ライブラリだけで動く。

μと分散パラメータαを固定し、発生確率p⁺を0.1・0.5・0.9へ変える。通常の負の二項分布とhurdle分布を同じμ、αで比較し、全確率と期待値を数値和で確認する。

## Results — 人工例の結果

ゼロを除くと平均が変わる。μ=2、α=0.5の通常の負の二項分布ではゼロ確率が0.25で、正の値に条件付けた平均は2.6667となる。p⁺=0.5のhurdle分布の平均は約1.3333。p⁺を変えても、正の量の条件付き平均は保たれる。

## What We Verified — 確認した範囲

CONFIRMED：分布の正規化、ゼロ確率の独立した操作、切詰め後の条件付き平均の補正。headの計算だけを確認したため、MechanismはPARTIAL。

## What We Did NOT Verify — 未検証の範囲

Performance / Scaling / Production applicabilityはNOT TESTED。Top-1 STEの学習、MoEの専門化、AR decoder、M5の精度は追試していない。欠品、fill rate、在庫費用は測っていない。

## Implementation — 実装

nb()は平均・分散パラメータ化の負の二項確率、hurdle()は正の領域を1−P_NB(0)で正規化する。0から999までの和で確率と平均を照合する。図は0から20までを表示し、残りの尾確率も示す。

## Original Paper / Official Code Mapping — 原典との対応

[式と図の説明](method.md)、[原典・実装対応表](mapping.md)、[実行結果](results.json)を参照。ページはlab.yamlとこれらのファイルから生成する。

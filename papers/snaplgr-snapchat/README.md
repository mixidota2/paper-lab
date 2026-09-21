# LLM-Based Generative Retrieval for Snapchat Content Recommendation

Qwen3-0.6BのCPT/SFTとTensorRT-LLMを組み合わせるSnapLGR。既存T5型GRとの7日A/BはView Time +0.37%。大きなoffline差と小さなonline差を分けて読む。

優先度: Watch。確認日: 2026-09-21。

## 実行

```sh
uv run papers/snaplgr-snapchat/run.py
uv run paper-lab build
```

## Overview

SnapLGRはQwen3-0.6Bを生成retrievalへ使うSnapchatの本番事例。既存の13M T5型GRに対し、7日間のオンラインA/BでView Time +0.37%。オフラインSID Recall@32の2.40倍という大きな差と、利用者体験の小さな相対改善を分けて読む。

## Problem

事前学習LLMは社内のSID語彙を知らない。SIDの衝突、語彙の意味付け、短い出力を広いbeamで生成する配信費用を同時に扱う必要がある。retrievalの改善だけでは、後段rankerを通過して最終体験に効く量は分からない。

## Core Idea

multimodal・PPR協調SID、CPTによる語彙grounding、CUDA beam searchと分散batch推論を組み合わせ、本番retrievalを改善した。

解釈: [SIDScope](sidscope-diagnostics.html)が扱う「有効SIDと一意itemの違い」を実配信で考える例になる。候補生成源の置換であり、[Sona](sona-yandex-music.html)の最終rankまでの統合とは責任範囲が違う。

## モデル / 手法

[method.md](method.md) の図と数式を読む。

## Why It Might Work

decoder-onlyの容量を増やすと履歴からSIDへ写す関数が豊かになる。PPRの協調信号は、見た目が近いだけでなく一緒に見られる動画をコード空間へ近付ける。CPTは初期の意味付けに役立つが、SFT後は行動信号で空間が変わる。語彙の意味が最後まで保存されるという単純な説明は、原典のRSA結果と合わない。

## Evidence

一次資料の著者報告。

[原典 Tables 1–8](https://arxiv.org/html/2607.28895v3)。7日A/BのView Time +0.37%（p=0.007）、Time Spent +0.09%（p=0.048）、Deep Sessions +0.18%（p=0.027）、Deep Sessions Unique User +0.11%（p=0.017）。割当traffic比率は確認した本文で示されていない。

online controlはCLIP型SID（256³）と13M T5で、treatmentはtokenizer・backbone・servingを同時に変える。LLM事前学習だけのオンライン効果ではない。offlineは同じQwen3-VL SIDへ固定して比較し、R@32はT5 4.624%、SnapLGR 11.11%。SID一致の指標であり、同じ率で動画を取得できるわけではない。

同じ0.6B規模でR@32はrandom+SFT 10.77%、pretrained+SFT 10.98%、CPT追加11.11%。CPT追加の相対利得は1.19%。text-grounding RSAは初期0.016→CPT 0.322→CPT+SFT 0.167となり、SFT onlyの0.162へ近付く。

推論throughputは1→9.3→30.7→45.7倍（A100）。訓練はA100上のsoftware最適化で1.78倍、H100への移行込みで3.63倍。hardware差をsoftwareだけの効果として紹介しない。

## Executable Understanding

30 SIDへ各2動画を割り当て、同じSID予測を「先頭動画」と「value最大動画」に展開する。正解をvalueと一致させた条件と逆にした条件を比較する。SID hitは両者で1.0でも、動画hitは変わる。valueがユーザーの正解と逆ならweighted側は失敗する反例も残す。

## Results

以下はこのLabの実行結果。上のEvidenceに載せた著者報告のA/Bとは、データも評価対象も異なる。

## What We Verified

Mechanism PARTIAL。SID-levelとitem-levelの評価の違い、materialization規則が結果に与える影響を確認した。valueを正解に一致させた人工条件での勝利を、SnapLGRの品質の証拠にしていない。

## What We Did NOT Verify

Performance / Scaling / Production applicabilityはNOT TESTED。QwenのCPT/SFT、PPR/RQ-VAE、TensorRT-LLM、分散worker、GPU speedup、実A/Bは未再現。toyのmax-valueは論文のvalue-weighted展開の簡略化で、本番の重みや候補budgetを再現していない。

## Implementation

`materialize()`はSIDから動画集合を引き、二つの選択規則を比較する。`compute()`は同じ生成SIDを固定し、正解との相関だけを反転する。LLMの学習をしていない点を実験タイトルにも反映した。

Python標準ライブラリだけで実行する。乱数を使う実験はseedを固定し、結果をコードと同じ場所に保存する。

## Original Paper / Official Code Mapping

[mapping.md](mapping.md)

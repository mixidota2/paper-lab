# RetailBench：個々の操作から180日の店舗運営へ

## Overview — 複数の業務を続けて動かす

RetailBenchは、価格・補充・棚・仕入先・資金繰りを180日間つなぐ店舗運営の評価環境である。

## Problem — 遅れた結果まで追えるか

Dominick’sのデータを基に96商品・20カテゴリを構成し、棚40商品、在庫容量15,000個、初期資金30,000、日額家賃600という条件で運営する。
需要やニュースの内部効果は隠される。

## Core Idea — 著者の主張と解釈

著者の主張：情報収集、仕入先選択、価格変更、補充を続ける過程で、不完全な情報収集、表面的な判断、継続する方策の欠如を診断する。

解釈：研究地図では運用中に店舗業務を操作するLLMの評価に当たり、InvEvolveの設計時の方策探索やSabreAgentの固定した在庫制御とは評価単位が異なる。

## Why It Might Work — 安い仕入れにも後の負担がある

解釈：安い仕入先を選んでも返品が増えれば収入は減り、棚へ載せなければ販売機会を失うため、ツール操作の正否だけでは長期の運営能力を測れない。

## Evidence — 選択実行の成績を読む

著者報告（v3 Table 1）。

| 選択実行 | 最終純資産 | 販売数量（個） | 生存日数 |
|---|---:|---:|---:|
| Oracle Policy | 131,510.42 | 267,998 | 180 |
| GPT-5.5 ReAct | 24,350.98 | 136,405 | 180 |
| DeepSeek-V4-Pro Plan-and-Act | 10,120.90 | 164,417 | 180 |

生存日数を優先し、同点なら純資産、販売数量の順で枠組みを選ぶため、これは全実行の平均ではない。
GPT-5.5はReActのみ。
Oracleは特権情報を使う。
Kimi-K2.6は130日、残る4モデルは58〜73日で終了した。

§4.3・Figure 3では、LLMの平均QualityFirstが21.5%、PriceFirstが55.6%、行動対象商品数が1日0.95〜7.89商品（Oracleは38.00商品）と報告される。
行動対象商品数と販売商品数は別の指標だ。

## Executable Understanding — 収支の結合を動かす

```sh
UV_CACHE_DIR=/tmp/uv-cache uv run --no-project papers/retailbench-long-horizon-store-agents/run.py
```

人工例では同じ需要・家賃の下で、安価だが返品率の高い仕入先と、割高だが返品率の低い仕入先を比較する。

| 人工設定 | PriceFirst | QualityFirst |
|---|---:|---:|
| 原価 | 4 | 5 |
| 返品率 | 30% | 5% |
| 価格 | 10 | 10 |
| 返品後の単位粗利 | 3 | 4.5 |

需要は対象商品当たり10個/日、初期現金3,000、期間30日、家賃600/日とし、毎日即時補充する。
これらは説明用の仮定である。

## Results — 対象商品数でも差が変わる

| 1日の対象商品数 | PriceFirstの最終現金 | QualityFirstの最終現金 |
|---|---:|---:|
| 8 | −7,800 | −4,200 |
| 38 | 19,200 | 36,300 |

## What We Verified

CONFIRMED：全240日分の収支恒等式。
MechanismはPARTIAL。

## What We Did NOT Verify

Performance / Scaling / Production applicabilityはNOT TESTED。
公式環境、LLM、納期、賞味期限、ニュース、需要の隠れた要因、棚内の代替効果は追試せず、負の現金でも計算を続けるため生存日数も再現しない。
実店舗のA/Bテストや棚割りの無作為化比較試験ではない。

## Implementation

run.pyは人工実験を計算し、Table 1の転記値と分けてresults.jsonへ保存する。
追加依存はない。
ページはlab.yamlと結果から生成する。

## Original Paper / Official Code Mapping

[対応表](mapping.md)に原論文の図表、公式コードへのリンク、省略点を記載した。
純資産の定義については、§3.3と付録の式(18)の記述差も残している。

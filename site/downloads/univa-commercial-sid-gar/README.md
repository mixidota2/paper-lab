# UniVA：広告の価値を、SID・枝選び・配信制約で揃える

UniVA: Unified Value Alignment for Generative Recommendation in Online Advertising at Tencent

広告の生成確率が高くても、配信できて収益につながるとは限らない。TencentのUniVAは商用属性をSIDの末尾へ入れ、生成と価値の2ヘッドを融合し、リクエスト別の有効な枝だけを探索する。WeChat ChannelsでGMV +1.50%を報告。実験比率はv1の5%からv2の20%へ記述が変わっており、版を区別して読む。

一次資料：[arXiv 2605.05803v2](https://arxiv.org/pdf/2605.05803v2)。判定：Must Read。

## 読み方

lab.yamlが本文と図の定義、method.mdがモデル・数式の補足、mapping.mdが一次資料との対応表。run.pyが最小実験、results.jsonが実行結果。siteは生成物である。

## 実行

```sh
uv run papers/univa-commercial-sid-gar/run.py
uv run paper-lab build
```

## 検証の境界

等頻度binの構成、固定価値を使うGARの加算、prefixごとの正規化、有効prefixのmask、beam幅と経路の関係を実行した。比較の入力と結果はresults.jsonに残す。

RQ-KMeans+、HSTU、MoE/MoR、PPO、MCTS、商用語彙の最適配分は学習・再現していない。実入札、配信filter、eCPM simulator、オンラインGMV、遅延、全カスケード削除は未検証。CSID更新に伴うbid変動、長期満足度、公平性も実験していない。

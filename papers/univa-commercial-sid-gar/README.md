# UniVA：生成した広告候補を価値と配信条件で選ぶ

UniVA: Unified Value Alignment for Generative Recommendation in Online Advertising at Tencent

生成する確率が高い広告でも、そのリクエストで配信できるとは限らず、収益につながるとも限らない。TencentのUniVAは、広告の識別子の末尾に入札額や広告主の目標に関する情報を入れる。候補の選択には生成のしやすさと見込まれる価値を使い、そのリクエストで表示できる広告だけを探索する。著者はWeChat ChannelsでGMV +1.50%を報告した。実験に使ったトラフィックの割合はv1では5%、v2では20%と記載されている。結果を参照するときは版を確認する。

一次資料：[arXiv 2605.05803v2](https://arxiv.org/pdf/2605.05803v2)。判定：Must Read。

## 読み方

本文と図は `lab.yaml`、モデルと数式の補足は `method.md`、原論文との対応は `mapping.md` にある。`run.py` を実行した結果は `results.json` に保存する。`site` はビルドで生成する。

## 実行

```sh
uv run papers/univa-commercial-sid-gar/run.py
uv run paper-lab build
```

## 検証の境界

入札額を件数が均等になる区間（bin）に分ける計算と、生成スコアに、固定した価値スコアを加えるGARの計算を実行した。各トークン列の途中（prefix）での正規化、選べないprefixの除外、beam幅を変えた場合に残る経路も確認した。比較の入力と結果は `results.json` にある。

RQ-KMeans+、HSTU、MoE/MoR、PPO、MCTS、商用語彙の最適配分は学習・再現していない。実際の入札、配信時の絞り込み（filter）、eCPM simulator、オンラインGMV、遅延、すべてのカスケード工程を取り除けるかは未検証。CSID更新に伴う入札額（bid）の変動、長期満足度、公平性も実験していない。

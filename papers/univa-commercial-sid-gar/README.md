# UniVA：生成した広告候補を価値と配信条件で選ぶ

UniVA: Unified Value Alignment for Generative Recommendation in Online Advertising at Tencent

Tencentの研究チームは、広告の内容が似ていても、入札額や広告主の目標が違えば、表示したときに見込まれる価値は変わると考えました。UniVAは、その違いを広告の識別子（SID）の末尾に表します。モデルが候補を選ぶときは、識別子を出す確率と、その候補がもたらす価値の予測を組み合わせます。その時点で配信できない広告につながる候補は、探索の途中で外します。

WeChat ChannelsのA/Bテストで、著者は完全な構成の取引総額（GMV）が従来方式より1.50%増えたと報告しています。この構成では学習方法と候補の選び方を一緒に変えており、どちらか片方の効果ではありません。同じ実験のトラフィックの割合は初版に5%、第2版に20%と記載され、変更の理由は本文からは分かりません。

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

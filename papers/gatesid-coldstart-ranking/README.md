# GateSID：商品情報と行動履歴を候補の順位付けに使う

Alibaba Internationalの研究チームは、クリックや購入の記録が少ない新商品を推薦候補の中でどう順位付けするかを調べました。GateSIDは、商品の画像や説明をもとにした識別子（SID）と、実際の行動から学んだ商品表現を使います。二つの表現で過去の行動を別々に参照し、掲載日数や表示回数などに応じて結果を混ぜます。GateSIDが変えたのは候補の順位付けで、候補を探す方法ではありません。

総トラフィックの20%を使った2週間のA/Bテストで、著者は従来方式より取引総額（GMV）が全体で2.6%、掲載20日未満の商品に限ると5.6%増えたと報告しています。追加の遅延は5ミリ秒未満でした。ただし、実験したのは一つのECサービスです。商品内容を表す特徴だけを加えた効果ではなく、GateSID全体を導入した結果です。

一次資料は[2603.22916v2.pdf](https://arxiv.org/pdf/2603.22916v2)。照合した節・表とPDFのSHA-256は[mapping.md](mapping.md)、計算の解説は[method.md](method.md)、サイト本文の原本は[lab.yaml](lab.yaml)を参照。

## 実行

```bash
uv run papers/gatesid-coldstart-ranking/run.py
```

この人工実験では、2組のattentionを求める前のスコア（logits）と履歴のベクトルを固定する。重みwを0から1まで動かし、混ぜたattentionを2種類の履歴に適用した結果と、同じwを掛けた対照損失（InfoNCE）を計算する。掲載日数などからwを学習する実験ではない。

## 検証範囲

MechanismはPARTIAL。何を確認できたか（CONFIRMED）、何を観測できなかったか（NOT OBSERVED）は[results.json](results.json)のchecksに記録した。Performance / Scaling / Production applicabilityはNOT TESTED。

固定したwで2組の重みが混ざることは確認した。RQ-VAEの学習、wを決めるモデルの学習、CTR・CTCVRの順位付け学習、AUC、本番のGMV、追加遅延の5ms制約は検証していない。新商品の推薦が本番で改善するかも、この実験からは判断できない。

## 実装の位置付け

確認した論文とarXivの書誌には、取得できる公式実装への案内を確認できなかった。公式コードを独立して実行していない（NOT TESTED）。非公開だと確認したわけではない。

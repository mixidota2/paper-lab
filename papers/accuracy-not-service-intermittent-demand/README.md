# 予測の誤差が小さくても、注文を完納できるとは限らない

論文：[Accuracy Is Not Service: A Decision-Aware Benchmark for Intermittent-Demand Forecasting](https://arxiv.org/abs/2609.13840)

需要がない月の多い部品について、著者は同じ補充規則で38の予測手法を比べた。20,330件の実注文では、予測精度が高い手法ほど、注文の全明細をそろえられる割合は低い傾向があった（順位相関ρ=−0.555）。別の実験では、Chronos-2の入力を整える方法を変えると、論文独自の誤差指標（MASE）は悪化したが、注文の完納率（COFR）は54%から63%に上がった。実験ごとに対象品目が違うため、在庫費用を含めて比較するには条件をそろえる必要がある。

[Labの解説ページ](https://mixidota2.github.io/paper-lab/papers/accuracy-not-service-intermittent-demand.html)

## 人工注文の実験を再実行する

```bash
uv run papers/accuracy-not-service-intermittent-demand/run.py
```

Pythonの標準ライブラリだけで動く。`run.py` が人工注文と正規化を実行し、`results.json` に結果が入る。解説は `lab.yaml` と `method.md`、原論文・公式コードとの対応は `mapping.md` にある。HTMLはリポジトリ直下で `uv run paper-lab build` を実行して生成する。

## Labで確認したこと

仕組みの一部を確認した（PARTIAL）。人工データでは、正規化した値を元に戻せること、すべてゼロの入力でも計算が有限になること、補充規則に従って在庫と完納を計算できることを確認した。また、初期在庫を増やすと完納率が下がる具体例も確認した（これらの条件ではCONFIRMED）。一方、144件の人工注文では、論文が報告した予測精度と完納率の順位の逆転は見られなかった（NOT OBSERVED）。

## Labで確認していないこと

予測性能、大規模データでの動作、実際の業務に使えるかは未検証（Performance / Scaling / Production applicability: NOT TESTED）。Chronos-2の学習済み重みを読み込んでいないため、正規化でモデルの予測がどう変わるかは確認していない。実注文の処理、RUFの生成、38手法の学習、再標本化による信頼区間の推定、在庫金額の最適化も行っていない。公開CSVでの計算は、著者が出した順位から相関を求め直したもので、非公開の実注文を使った追試ではない。

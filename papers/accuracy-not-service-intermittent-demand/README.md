# Accuracy Is Not Service: A Decision-Aware Benchmark for Intermittent-Demand Forecasting

著者が38手法を20,330件の注文で比較したところ、予測精度と注文を完納できた割合の順位相関はρ=−0.555だった。Chronos-2の入力の正規化を変更すると、論文で定義した誤差指標（MASE）は悪化したが、全明細をそろえて納められた注文の割合（COFR）は54%から63%へ上がった。実験ごとに対象品目が異なるため、在庫費用と合わせて比較条件を確認する必要がある。

公開ページ: https://mixidota2.github.io/paper-lab/papers/accuracy-not-service-intermittent-demand.html

## 実行

```bash
uv run papers/accuracy-not-service-intermittent-demand/run.py
```

Python標準ライブラリだけを使う。`lab.yaml` と `method.md` が解説の原本、`run.py` が最小実験、`results.json` が出力、`mapping.md` が原典との対応。HTMLは `uv run paper-lab build` で生成する。

## 検証範囲

仕組みの確認は一部に限られる（PARTIAL）。このLabでは、正規化した値を元に戻せること、入力がすべてゼロでも計算値が有限になること、同じ補充規則の下で在庫の増減と注文の完納を判定する処理を確認した。また、目標在庫を増やしても、完納できる注文の割合が必ず上がるわけではない例を確認した。これらの限定した条件は確認済み（CONFIRMED）だが、人工データの再計算では、論文が報告した予測精度と完納率の順位逆転は見られなかった（NOT OBSERVED）。

Performance / Scaling / Production applicability NOT TESTED。Chronos-2の重みをロードせず、内部表現の変化による改善は検証していない。実注文・RUF生成・38手法の学習、bootstrap CI、在庫金額の最適化も未実行。CSVの順位再計算は凍結集計の算術監査であり、機密panelの追試ではない。

# Accuracy Is Not Service: A Decision-Aware Benchmark for Intermittent-Demand Forecasting

38手法・20,330注文で精度順位と注文充足順位のρ=−0.555。Chronos-2の正規化修正はMASEを悪化させつつCOFRを54→63%へ改善した。指標の母集団と在庫費用を分けて読む。

公開ページ: https://mixidota2.github.io/paper-lab/papers/accuracy-not-service-intermittent-demand.html

## 実行

```bash
uv run papers/accuracy-not-service-intermittent-demand/run.py
```

Python標準ライブラリだけを使う。`lab.yaml` と `method.md` が解説の原本、`run.py` が最小実験、`results.json` が出力、`mapping.md` が原典との対応。HTMLは `uv run paper-lab build` で生成する。

## 検証範囲

Mechanism PARTIAL。正規化の往復と全ゼロ時の有限性、同一policyの在庫保存・補充・完納判定、stock target増加がCOFR単調増加を保証しない反例を確認。局所条件はCONFIRMED。人工replayの精度逆転はNOT OBSERVED。

Performance / Scaling / Production applicability NOT TESTED。Chronos-2の重みをロードせず、内部表現の変化による改善は検証していない。実注文・RUF生成・38手法の学習、bootstrap CI、在庫金額の最適化も未実行。CSVの順位再計算は凍結集計の算術監査であり、機密panelの追試ではない。

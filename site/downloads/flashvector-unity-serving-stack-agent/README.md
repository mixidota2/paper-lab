# FlashVector: Agent for Hierarchical Model Serving Stack Optimization

UnityのFlashVectorはNsight/eBPFの測定から層ごとの変更を提案し、本番traffic replayで全体のthroughputとlatencyを検証する。model serverは最大2× throughput・1.98× latency speedup、feature処理は約1.6×。局所速度と採択条件を分けて読む。

## 問い

kernelが速くなっても、配信全体が速くならなければ棄却できるか

## 再実行

```bash
uv run papers/flashvector-unity-serving-stack-agent/run.py
```

Python標準ライブラリだけを使う。単体で取得した場合は `uv run run.py`。結果はスクリプトと同じ場所の `results.json` に保存する。

## 読む順序

`lab.yaml` の問題設定・根拠、`method.md` の仕組みと図、`run.py` と `results.json`、`mapping.md` の省略点。HTMLは `uv run paper-lab build` で生成する。

Mechanism PARTIAL。Performance / Scaling / Production applicability NOT TESTED。小実験で確認した局所条件のみCONFIRMEDとし、論文の本番数値を再現したとは扱わない。

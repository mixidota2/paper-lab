# UniPinRec — 小実験

`uv run papers/unipinrec/run.py` は合成 session で history prefill と cache hit を数え、`results.json` を更新する。Pinterest の GPU serving や online A/B test の再現ではない。

原論文 §3.1 の MAM、§3.3 の KV 共有、§4.2 の latency 比較を、再計算量の小さな会計モデルへ対応づけた。

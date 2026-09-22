# Verify, Don’t Trust: Agentic Model Development for Video Discovery Retrieval at Scale

37日間のVDD研究で、−22 ppという誤った比較をhuman gateが棄却。評価器修正後、matched-lineageで+3.20 pp、別の7日A/BでGSRR +0.66%相対差。

公開ページ: https://mixidota2.github.io/paper-lab/papers/evopilot-verify-dont-trust-autoresearch.html

## 実行

```bash
uv run papers/evopilot-verify-dont-trust-autoresearch/run.py
```

Python標準ライブラリだけを使う。`lab.yaml` と `method.md` が解説の原本、`run.py` が最小実験、`results.json` が出力、`mapping.md` が原典との対応。HTMLは `uv run paper-lab build` で生成する。

## 検証範囲

Mechanism PARTIAL。実現Kの反証probeと、pairの許可外差分・no-op・欠落の拒否は人工artifactでCONFIRMED。canonical recordのhashも計算する。

Performance / Scaling / Production applicability NOT TESTED。本番MBR学習、数億動画index、37日agent運用、offline +3.20 pp、online +0.66%は再現していない。local hashは遠隔artifactの真正性を保証しない。

# UniPinRec — Interactive Lab

Hanyu Li et al. (Pinterest), arXiv:2606.00422（2026）。retrieval と ranking の
full-stack 統合（ANN 維持・MAM・KV 再利用）のラボ。

## 履歴エンコードの共有がサービングの本質

- MAM がインターリーブより系列を膨らませない理由（長さの玩具）
- ANN を残したまま L0+L1 を統合する現実的な道筋

## やっていないこと

本番 A/B や Hit@3 学習は再現しない。

```bash
uv run python papers/unipinrec/run.py
```

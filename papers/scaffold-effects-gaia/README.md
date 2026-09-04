# Scaffold Effects on GAIA — Interactive Lab

Jason Starace, arXiv:2606.08529（2026）。事前登録つきで、同一モデルの GAIA 精度が
scaffold だけで大きく動くことを示した論文のラボ。

## このラボで分かること

- 評価単位を「モデル」ではなく harness–model 組として読む理由
- 構造化 scaffold が「行動は少ないが中盤失敗からの復帰は高い」方向であること（玩具）

## 動かないこと / やっていないこと

GAIA 本体、5モデル API、コスト表、H1–H4 の統計再現はしない。`run.py` は合成タスクだけ。

```bash
uv run python papers/scaffold-effects-gaia/run.py
```

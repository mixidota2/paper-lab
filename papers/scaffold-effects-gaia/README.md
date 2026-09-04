# Scaffold Effects on GAIA — Interactive Lab

Jason Starace, arXiv:2606.08529（2026）。事前登録つきで、同一モデルの GAIA 精度が
scaffold だけで大きく動くことを示した論文のラボ。

## 評価単位は harness–model の組

- 公開数字をモデル属性として読むと誤る理由が、制御比較で見える
- 構造化 scaffold は「行動は少ないが中盤失敗からの復帰は高い」方向（玩具）

## 動かないこと

GAIA 本体、5モデル API、コスト表、H1–H4 の統計再現はしない。`run.py` は合成タスクだけ。

```bash
uv run python papers/scaffold-effects-gaia/run.py
```

# VARG: Value-Aware and Ranking-Aligned Generative Retrieval for Dynamic E-commerce Search

Tmall Appの生成チャネルは予約枠でpre-rankを迂回し、既存final rankerへ渡す。14日・検索traffic 20%のA/BでGMV +1.45%。初期の衝突ゼロと日次の住所固定は別の約束。

公開ページ: https://mixidota2.github.io/paper-lab/papers/varg-tmall-value-generative-retrieval.html

## 実行

```bash
uv run papers/varg-tmall-value-generative-retrieval/run.py
```

Python標準ライブラリだけを使う。`lab.yaml` と `method.md` が解説の原本、`run.py` が最小実験、`results.json` が出力、`mapping.md` が原典との対応。HTMLは `uv run paper-lab build` で生成する。

## 検証範囲

Mechanism PARTIAL。Eq. 6の範囲切り詰め、既存住所の不変性、item単位の衝突率、報酬gate、LO端点の正規化を人工fixtureで確認した。これらの局所不変条件はCONFIRMED。

Performance / Scaling / Production applicability NOT TESTED。RQ-VAE・Q2I表現、Qwen2.5の学習、GRPOの収束、51.43M商品でのslot負荷、GMV・HRの再現はしていない。日次更新後も全IDがcollision-freeという主張は原論文にもない。

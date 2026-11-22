# VARG: Value-Aware and Ranking-Aligned Generative Retrieval for Dynamic E-commerce Search

Tmall Appでは、生成モデルが選ぶ候補に専用の枠を用意した。この候補は予備の順位付け（pre-rank）を省き、既存の最終順位付けモデル（final ranker）に直接渡す。検索トラフィックの20%を使った14日のA/Bテストで、著者はGMV +1.45%を報告した。初期に商品同士で識別子が重ならないことと、日次更新で既存商品の識別子を変えないことは、別の条件。

公開ページ: https://mixidota2.github.io/paper-lab/papers/varg-tmall-value-generative-retrieval.html

## 実行

```bash
uv run papers/varg-tmall-value-generative-retrieval/run.py
```

Pythonの標準ライブラリだけを使う。解説の原本は `lab.yaml` と `method.md`、最小実験は `run.py`、実験結果は `results.json`、原典との対応は `mapping.md` にある。HTMLは `uv run paper-lab build` で生成する。

## 検証範囲

MechanismはPARTIAL。人工データで、Eq. 6が値を所定の範囲に収めること、既存の識別子が変わらないこと、商品単位の衝突率、報酬を与える条件、LOで端点の確率を正規化する計算を確認した。確認済み（CONFIRMED）なのは、これら個別の条件に限る。

Performance / Scaling / Production applicabilityはNOT TESTED。RQ-VAE・Q2I表現、Qwen2.5の学習、GRPOの収束、51.43M商品でのslot負荷は検証せず、GMV・HRも再現していない。日次更新後もすべてのIDが重複しないとは、原論文も主張していない。

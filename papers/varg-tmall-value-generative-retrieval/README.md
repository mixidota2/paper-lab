# VARG: Value-Aware and Ranking-Aligned Generative Retrieval for Dynamic E-commerce Search

Taobao・Tmallの研究チームは、検索の意図に合い、購入にもつながる商品を、生成モデルで早い段階から探す方法を提案しました。VARGは、検索文との関連性、過去のクリックや購入、既存の順位付けモデルの評価を学習に使います。生成した商品は、通常の予備順位付けを通さず、確保した枠から既存の最終順位付けへ渡します。最終順位付けまで置き換える方法ではありません。

Tmallアプリの検索トラフィックの20%を使った14日間のA/Bテストで、著者は従来方式より取引総額（GMV）が1.45%、利用者あたりの閲覧指標（IPV/user）が0.22%増えたと報告しています。この比較では学習方法と候補を渡す経路をまとめて変えており、商品IDの学び方だけの効果は分かりません。

公開ページ: https://mixidota2.github.io/paper-lab/papers/varg-tmall-value-generative-retrieval.html

## 実行

```bash
uv run papers/varg-tmall-value-generative-retrieval/run.py
```

Pythonの標準ライブラリだけを使う。解説の原本は `lab.yaml` と `method.md`、最小実験は `run.py`、実験結果は `results.json`、原典との対応は `mapping.md` にある。HTMLは `uv run paper-lab build` で生成する。

## 検証範囲

MechanismはPARTIAL。人工データで、Eq. 6が値を所定の範囲に収めること、既存の識別子が変わらないこと、商品単位の衝突率、報酬を与える条件、LOで端点の確率を正規化する計算を確認した。確認済み（CONFIRMED）なのは、これら個別の条件に限る。

Performance / Scaling / Production applicabilityはNOT TESTED。RQ-VAE・Q2I表現、Qwen2.5の学習、GRPOの収束、51.43M商品でのslot負荷は検証せず、GMV・HRも再現していない。日次更新後もすべてのIDが重複しないとは、原論文も主張していない。

# SIDInspector: A Mapping-First Diagnostic Resource for Semantic-ID Tokenizers

商品と識別子の対応表を共通の形式にそろえ、識別子の使われ方、複数商品への重複割当、行動が似た商品のまとまり、人気別の割当、索引の構造を別々に調べる。collision-freeでも意味のあるprefixとは限らない。

公開ページ: https://mixidota2.github.io/paper-lab/papers/sidinspector-mapping-diagnostics.html

## 実行

```bash
uv run papers/sidinspector-mapping-diagnostics/run.py
```

Python標準ライブラリだけを使う。`lab.yaml` と `method.md` が解説の原本、`run.py` が最小実験、`results.json` が出力、`mapping.md` が原典との対応。HTMLは `uv run paper-lab build` で生成する。

## 検証範囲

Mechanism PARTIAL。人工入力の契約違反拒否、非singleton bucketに属するitem比率、重み付き近傍回収、tailの一意SID比率、prefix数とfan-outを確認。局所計算はCONFIRMED。

Performance / Scaling / Production applicability NOT TESTED。公式packageの全gate、GRID/ReSID/LETTER/LC-Rec export、co-occurrence構築のsampling、generatorのRecall/NDCG、latencyとonline A/Bは未実行。D2の衝突率だけから衝突の害を判断しない。

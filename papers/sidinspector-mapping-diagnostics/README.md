# SIDInspector: A Mapping-First Diagnostic Resource for Semantic-ID Tokenizers

このLabでは、各商品が異なるSemantic ID（SID）を持つことと、一緒に選ばれやすい商品がSIDの先頭を共有することを分けて調べます。同じ6商品の架空の対応表を比べると、全商品を区別できても、関連する商品が同じグループに残るとは限らないことが分かります。

公開ページ: https://mixidota2.github.io/paper-lab/papers/sidinspector-mapping-diagnostics.html

## 人工例を動かす

```bash
uv run papers/sidinspector-mapping-diagnostics/run.py
```

Python標準ライブラリだけで動きます。実行コードは `run.py`、計算結果は `results.json` にあります。手法を読むなら `method.md`、論文初版との対応を確かめるなら `mapping.md` を開いてください。公開ページは `lab.yaml` と手法の説明 `method.md` を使って生成します。サイト全体は `uv run paper-lab build` で生成できます。

## 何を確かめたか

人工データから、SIDを共有する商品の割合、先頭の符号が一致する商品対の重み付き割合、不人気側の商品に割り当てられた異なるSIDの比率、符号列の数と分岐数を計算しました。商品IDの重複や商品登録の漏れも検出します。確かめたのは局所計算で、論文の仕組み全体ではありません（PARTIAL）。

[論文初版](https://arxiv.org/pdf/2606.10375v1)にある公式パッケージの検証や、各方式の対応表の再出力は行っていません。利用履歴からの商品対の選び直し、生成モデルのRecallやNDCG、応答時間、A/Bテストも未実施です。重複が多いという結果だけで、推薦が悪化したとは判断できません。

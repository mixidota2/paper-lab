# QuaSID：似たSIDを持つ商品を、学習でいつ引き離すか

QuaSIDの著者は、異なる商品のSemantic ID（SID）が重なる問題に取り組んだ。同じ商品や、行動履歴から近付ける対象にした組は引き離さない。それ以外では、全桁が一致する組を、一部の桁だけが一致する組より遠くに離すよう学習する。ベクトルが離れてもSIDの一意性は保証されない。

Kuaishouの著者は、順位付けにSID由来の特徴量を加えると、あるシナリオの取引総額（GMV-S2）が対照より2.38%増えたと報告した。一方、候補取得でSIDの作り方を変えた試験では、公開後48時間の再生が100回未満の動画で完了注文数が対照より6.42%増えた。指標、対象、変更した段階が違うので、二つの数値は直接比較できない。

## 実行

```bash
uv run papers/quasid-collision-qualified-sid/run.py
uv run paper-lab build
```

`run.py`はPythonの標準ライブラリだけを使い、スクリプトと同じフォルダーに`results.json`を書き出す。Labリポジトリの外で配布ファイルを動かすなら、出力先を上書きしてよいフォルダーに置いてから`python3 run.py`を実行する。

## ファイルと確認の範囲

`lab.yaml`が記事と図の定義、[method.md](method.md)が手法、[mapping.md](mapping.md)が論文と実験の対応を収める。Labは架空の例で除外条件と距離の計算を確かめた（Mechanism PARTIAL）。論文のモデルは学習していない。推薦の性能、規模を大きくした場合の挙動、本番への適用は未検証（NOT TESTED）。CONFIRMEDは`results.json`に記録した個別の計算に限る。

[論文初版の全文](https://arxiv.org/html/2603.00632v1)。元記事の出典確認日：2026-09-15。

# Stop Treating Collisions Equally: Qualification-Aware Semantic ID Learning for Recommendation at Industrial Scale

QuaSIDは、商品を表す離散コード（Semantic ID、SID）が重なったとき、学習で表現ベクトルを引き離す組を選ぶ。同じ商品どうしの組と、行動履歴から近付けるべきだと判定した組（協調正例）は、引き離す対象から外す。そのうえで、IDの全桁が一致する組と、一部の桁が異なり、その数が半径 R 以下の組で、表現ベクトルのコサイン距離に求める下限を変える。害のある衝突を減らす方法であり、衝突がゼロになることは保証しない。

Kuaishouのオンライン比較では、順位付け（ranking）にSIDの特徴を加えた場合にGMV-S2が+2.38%だったと著者が報告している。候補取得（retrieval）では、公開後48時間の再生が100回未満の動画（100vv群）で完了注文数が+6.42%だった。評価指標も対象も異なり、どちらもLabで再現した結果ではない。

## 実行

```bash
uv run papers/quasid-collision-qualified-sid/run.py
uv run paper-lab build
```

実験コードはPython標準ライブラリだけを使う。どのディレクトリから実行しても、`run.py` と同じフォルダーの `results.json` を更新する。

## 原本

`lab.yaml` に本文と図の定義、`method.md` に手法、`mapping.md` に原論文との対応を記す。HTMLは生成ツールで作る。合成実験のコードと結果は `run.py` と `results.json` にある。

## 検証範囲

Labでは仕組みの一部を確認した（Mechanism PARTIAL）。性能、規模を大きくした場合の挙動、本番への適用は試していない（Performance / Scaling / Production applicability NOT TESTED）。CONFIRMEDは、JSONに記した個別の算術と比較条件だけを指す。原論文のモデルは学習していない。

[一次資料・全文](https://arxiv.org/html/2603.00632v1)。確認日：2026-09-15。未検証の項目や出典を読む際の注意は、Labの本文と `mapping.md` を参照。

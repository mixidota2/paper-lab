# 最終品揃えを決めるための観測計画

一次資料は The Value of Experiments in Assortment Optimization, arXiv:2610.40557v1 (2026-10-29) です。Labの説明・図・コードは自作です。原論文の本文や図は配布せず、著者コードを再現したとは主張しません。

リポジトリで依存関係を固定してから次の順に実行します。

```sh
uv sync --locked --extra dev --python 3.12
uv run --locked python papers/assortment-observation-budget/run.py
uv run --locked pytest tests/test_assortment_observation.py -q
uv run --locked pytest -q -ra --fail-on-skip
uv run --locked paper-lab build --out dist/assortment-preview
uv run --locked python tests/review_103.py --preflight --site dist/assortment-preview --out /tmp/assortment-preflight-new
```

配布する `run.py` はPythonの標準ライブラリだけで単独実行でき、同じフォルダに余分な空白のない `results.json` を再生成します。生成前に、4通りの選好、8通りの観測数、3通りの収益倍率を組み合わせた96条件に固定しました。観測数mは2〜9で、Cで起こりうる観測経路は最大1296通りです。乱数は使わないのでseedもありません。

Aでは、正の有理数で表した重複のない収益を大きい順に与えます。画面では6候補から選びます。BとCは収益が `(3a,2a,a)` で、aが正の場合だけ扱います。Bはm≤128、Cは⌊m/2⌋≤4に制限し、条件を外れた入力は累乗や経路の列挙に入る前に拒みます。これは教材の計算量を抑える制限であって理論上の上限ではありません。極端に桁数の多い分数まで安全に処理できる保証はありません。統合画面では、m≤9の計算済み条件から選びます。

- **確認済み（CONFIRMED）**：有限例の有理数計算、確率の合計、観測数、閾値ちょうどの場合と同率の場合、再生成結果と配布ファイルの一致、JavaScriptでの選択規則とリセットの自動検査。
- **一部確認（PARTIAL）**：論文の規則との対応は確認しましたが、すべての証明を独立に検証したわけではありません。
- **未確認（NOT OBSERVED）**：著者の実装、原文ファイルのローカルでのバイト列とハッシュ、以前のLibrary入力。
- **未検証（NOT TESTED）**：実店舗での効果、未知の分布での性能、大規模実行、手動でのブラウザー表示や実機の表示。複数の画面幅向けのCSSは静的な自動検査を行いましたが、描画された画面のピクセルは確認していません。

事前検査（preflight）の出力先には未使用のフォルダを指定し、過去の検証記録は上書きしません。

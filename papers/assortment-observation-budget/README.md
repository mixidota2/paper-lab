# 最終品揃えを決めるための観測計画

同じ品揃えを提示する顧客を増やす場合と、提示する品揃えの種類を増やす場合を比較する教材です。一次資料は [The Value of Experiments in Assortment Optimization](https://arxiv.org/html/2610.40557v1)（arXiv:2610.40557v1、2026-10-29）です。Labが説明、図、コードを作成しました。論文の本文や図は配布しておらず、著者コードの再現も行っていません。

リポジトリのルートで固定済みの依存関係を入れ、計算、テスト、サイト生成、事前検査の順に実行してください。

```sh
uv sync --locked --extra dev --python 3.12
uv run --locked python papers/assortment-observation-budget/run.py
uv run --locked pytest tests/test_assortment_observation.py -q
uv run --locked pytest -q -ra --fail-on-skip
uv run --locked paper-lab build --out dist/assortment-preview
uv run --locked python tests/review_103.py --preflight --site dist/assortment-preview --out /tmp/assortment-preflight-new
```

配布する `run.py` はPythonの標準ライブラリだけで動きます。このファイルを単独で実行しても、同じフォルダに余分な空白のない `results.json` を再生成できます。計算するのは4通りの選好、8通りの観測数、3通りの収益倍率を組み合わせた96条件です。観測数mは2〜9で、Cでは最大1296通りの観測経路を計算します。経路を列挙するので、乱数とその初期値（seed）は使いません。

Aでは、正の有理数で表した同額のない商品収益を大きい順に与えてください。画面では6通りから選べます。BとCは収益が `(3a,2a,a)` でaが正の場合だけ扱います。コードが扱う上限は、Bではm≤128、Cでは⌊m/2⌋≤4です。コードはこの条件を外れた入力を、累乗や経路の列挙を始める前に拒みます。この制限は教材の計算量を抑えるためのもので、論文の理論上の上限ではありません。桁数が極端に多い分数まで処理できる保証はありません。AとB・Cを比べる画面は、m≤9の計算済み条件を使います。

- 確認済み（CONFIRMED）：有限例の有理数計算、確率の合計、観測数、閾値と等しい場合、同率の場合、再生成結果と配布ファイルの一致を確認しました。JavaScriptで品揃えを選ぶ処理と初期条件へのリセットは自動テストで確認しました。
- 一部確認（PARTIAL）：論文の規則と実装の対応は確認しました。すべての証明を独立に検証したわけではありません。
- 未確認（NOT OBSERVED）：著者の実装、原文ファイルのローカルでのバイト列とハッシュ、以前のLibrary入力は確認できていません。
- 未検証（NOT TESTED）：店舗での効果、未知の分布での性能、大規模実行、ブラウザーでの手動表示や実機の表示は検証していません。複数の画面幅を想定したCSSを静的な自動テストで確認しましたが、実際に描画した画面のピクセルは確認していません。

事前検査（preflight）の出力先には未使用のフォルダを指定してください。過去の検証記録は上書きしません。

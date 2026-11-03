# 品揃えの観測予算を分けるLab

一次資料：The Value of Experiments in Assortment Optimization, arXiv:2610.40557v1 (2026-10-29)。自作の説明・図・コードです。原論文本文・図を配布せず、著者コードの再現を主張しません。

リポジトリの固定依存を準備してから実行します。

```sh
uv sync --locked --extra dev --python 3.12
uv run --locked python papers/assortment-observation-budget/run.py
uv run --locked pytest tests/test_assortment_observation.py -q
uv run --locked pytest -q -ra --fail-on-skip
uv run --locked paper-lab build --out dist/assortment-preview
uv run --locked python tests/review_103.py --preflight --site dist/assortment-preview --out /tmp/assortment-preflight-new
```

run.pyは標準ライブラリだけで動き、同じ場所のresults.jsonをcompact JSONとして再生成します。配布run.pyは単独で動きます。96条件＝4選好×8予算×3倍率。Cの最大有効経路数は1296、mは2〜9。乱数もseedもありません。生成前にこの予算を固定しました。

Aは正の厳密降順の有理数列。画面は6候補に限定。B/Cは(3a,2a,a)の正倍率のみ。Bの厳密二項計算はm≤128、Cは⌊m/2⌋≤4で累乗・列挙前に拒否します。これは教材の資源制限で、理論上限ではありません。任意巨大分数のビット長まで安全という保証はしません。統合UIはm≤9で計算済み条件だけを選びます。

CONFIRMED：有限例の有理数計算、確率和、予算、等号・同率、再生成と配布一致、JSの選択規則とresetの自動検査。
PARTIAL：論文の規則との対応。全証明は独立検証していません。
NOT OBSERVED：著者実装、ローカル原本文bytes/hash、以前のLibrary入力。
NOT TESTED：実店舗効果、未知分布での性能、大規模実行、手動ブラウザー・実機の表示。複数幅は静的CSS契約を自動検査し、画面ピクセル検証と区別します。

preflightの出力先は未使用のディレクトリを指定します。既存の検証証拠を上書きしません。

# TRACE：実行が変わったのか、採点が変わったのか

この教材では、在庫を8から5に直すスクリプトを使います。同じ操作を別名で呼ぶと、元の名前しか見ない採点器は点を下げます。採点器が別名を元の名前に読み替えれば、実行をやり直さずに点数が戻ります。スクリプトが書き込みを省いた場合は、名前を読み替えても在庫は直りません。

## 教材を再実行する

リポジトリのルートで次のコマンドを実行します。最初に開発用の依存関係をそろえ、次に教材を検査します。最後のコマンドで `results.json` と `experiment.md` を作り直します。

```bash
uv sync --extra dev --frozen
uv run papers/trace-verifier-brittleness/run.py --test
uv run papers/trace-verifier-brittleness/run.py
```

`results.json` の `reported` は著者が報告した数値、`synthetic` はLabが作った在庫の記録です。Pythonは標準ライブラリを使い、3種類のスクリプトと2種類ずつの名前・採点方法を組み合わせた12条件を計算します。ブラウザーは条件を切り替えて表示します。著者のコードやモデルAPIは実行しません。

## 表示と数値を検査する

ビルドは指定先を作り直します。既存のサイトを上書きしないよう新しいディレクトリを用意し、全記事を入力にします。

```bash
review_dir=$(mktemp -d "${TMPDIR:-/tmp}/paper-lab-trace.XXXXXX")
uv run --locked paper-lab build --out "$review_dir/site"
uv run --locked python tests/review_103.py --preflight \
  --site "$review_dir/site" --out "$review_dir/preflight"
uv run python -m http.server --directory "$review_dir/site" 8000
```

ローカルで `/papers/trace-verifier-brittleness.html` を開くと、条件と採点方法を切り替えられます。名前をそろえた操作列と最終状態のハッシュも表示できます。JavaScriptを無効にすると、最初の条件だけを読めます。

`tests/test_trace_lab.py` はPythonの4件のテストと、生成した二つのファイルが保存版と一致するかを確認します。`tests/test_trace_integration.py` はNodeで12条件と初期化を検査します。Nodeでは画面の代用品を使うので、実際の表示や操作は別に調べます。

現行のPRワークフローは、pytest、全記事の生成、静的preflightに加え、署名とサンドボックスを確認したChromeを使います。TRACEのブラウザー検査は360・390・768・1440ピクセルの幅で、点数、操作、ハッシュ、棒の幅、初期化、キー操作、JavaScript無効時の初期表示を確認します。保護を確認できない環境では設定を変更して続けません。この説明は、手元でブラウザー検査を終えたという意味ではありません。

## 確認できた範囲

名前だけを替えた条件では操作と最終状態が一致し、再採点で点だけが戻りました。書き込みを省いた条件では失敗が残ります。Labは論文の手順の一部を架空の在庫で確認しました。著者のStudy 2・3の再計算、言語モデルのばらつき、採点の正確さ、本番での性能は未検証です。

[一次資料：Radhika Gaonkar、TRACE v1（2026年10月8日）](https://arxiv.org/abs/2610.11678v1)。論文はCC BY-NC-SA 4.0です。著者の図版、本文やコードを転載せずに自作例を作りました。図1・2、表6・8との関係は `mapping.md` に記載しています。

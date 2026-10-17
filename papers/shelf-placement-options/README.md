# 吊り・棚置きと棚板高さ

独自の1商品8候補と、全幅2商品の18候補を比較する。原著の大規模探索・実験表を再現したものではない。説明は承認済み原稿を基にし、実行状態を更新した。

```bash
uv run --locked papers/shelf-placement-options/run.py
uv run --locked --extra dev pytest tests/test_shelf_placement.py -q
uv run --locked python -m paper_lab.build --out /tmp/paper-lab-shelf-preview
uv run --locked python -m http.server 8000 --directory /tmp/paper-lab-shelf-preview
```

/papers/shelf-placement-options.html を開く。単体は /downloads/shelf-placement-options/interactive.html。model.jsとinteractive.jsを同じ場所へ置く。Pythonは標準ライブラリのみ。

実験1: ν≤1は吊り2面12√2、ν>1は棚置き4面16。実験2: 固定18√2、可変10√2+8√3、固定案比9.988661%。全て合成値。

幾何判定はPythonでFractionによる有理数比較。ブラウザーの寸法は画面の0.1刻みに合わせた整数単位で計算し、保存した十進表記を有理数検査へ渡す。利益計算は浮動小数点。目的値比較も絶対1e−10で、表示値で判定しない。最適解数は面数・置き方・上下順の候補数であり、同利益の連続座標全体の個数ではない。

全幅2商品なので、下商品の高さ＋余白＋板厚まで支持面を下げれば上商品を置ける可能性は失わない。自由配置一般の粗い格子探索を厳密だと主張しない。3種の商品が同居する採用品と面数を同時に選ぶ人工例は初版対象外。

CONFIRMED: 合成例の計算と座標検査。原論文の仕組みの確認は一部のみ（PARTIAL）。実店舗・性能・規模・実ブラウザーは未検証（NOT TESTED）。著者コードと補足の設定は未確認（NOT OBSERVED）。

追加検査：候補とは別の不変な商品定義を `check(layout, spec)` へ渡し、重複ID、不正面数・寸法・置き方・上限を拒否する。UIの3,562設定（Aの余白×β全域、Bの可変棚板で余白×厚さ全域、固定棚板の1,000標本）について、全候補をPythonの有理数検査と照合する。任意の商品や横列・回転を扱う一般モデルは検証対象外。

図と操作文言の分岐は `uv run --locked --extra dev pytest tests/test_shelf_ui.py -q` で確認できる。DOMの代替を使ったソース検査であり、実ブラウザーの描画・画面幅・操作・ダウンロードの検証ではない。

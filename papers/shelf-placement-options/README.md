# 置き方と棚板の高さで、商品が何面入るかを比べる

商品をフックに掛けると、1面を見せたときによく売れると仮定します。それでも、取り出す隙間で面数が減れば、棚板に並べた方が利益は高くなります。この教材では、棚の全幅を使う1商品の8候補と、棚板を1枚入れた2商品の18候補を比べます。どの案でも全商品を置きます。

```bash
uv run --locked papers/shelf-placement-options/run.py
uv run --locked --extra dev pytest tests/test_shelf_placement.py -q
uv run --locked python -m paper_lab.build --out /tmp/paper-lab-shelf-preview
uv run --locked python -m http.server 8000 --directory /tmp/paper-lab-shelf-preview
```

記事は `/papers/shelf-placement-options.html`、実験だけを見る場合は `/downloads/shelf-placement-options/interactive.html` を開きます。実験ファイルと同じ場所に `model.js` と `interactive.js` を置きます。Pythonの計算は標準ライブラリだけで動きます。

実験1では、余白νが1以下なら吊り2面の利益12√2が最大です。νが1を超えると、棚置き4面の利益16が最大になります。実験2では、棚板を固定すると18√2、高さも選ぶと10√2+8√3です。差は固定案に対して9.988661%です。すべて教材用の数値です。

Pythonは、寸法と座標の比較に `Fraction` を使います。画面の計算は0.1刻みの寸法を整数に換算し、保存した十進表記をPythonの検査へ渡します。利益は浮動小数点で計算し、丸めた表示ではなく、絶対差1e−10以内を同率と判定します。同率数が数えるのは面数・置き方・上下の順番の候補であり、連続した位置の総数ではありません。

2商品はそれぞれ全幅を使うため、板の上面を「下の商品高＋余白＋板厚」まで下げても、上の商品が収まる可能性は失われません。この性質を自由配置一般には使えません。また、三つの商品から何を残し何面ずつ置くかを同時に選ぶ実験は含めていません。

検査関数 `check(layout, spec)` には、計算が作った候補と商品定義を別々に渡します。重複ID、不正な面数、寸法、置き方を拒否します。3,562設定について、画面が作った全候補をPythonの有理数検査と照合します。対象は実験1の余白×β全域、実験2の棚板可変案の余白×板厚全域、固定案の1,000標本です。任意の商品や横列、回転は検証していません。

合成例の計算と座標検査はCONFIRMED、原論文の仕組みとの対応はPARTIALです。実店舗の結果、性能、規模、実ブラウザーはNOT TESTED。著者コードと補足の設定はNOT OBSERVEDです。図と操作文の分岐は `uv run --locked --extra dev pytest tests/test_shelf_ui.py -q` で確認できますが、DOMを代用した検査であり、画面幅、描画、ダウンロードを実ブラウザーで確かめたわけではありません。

## 読む順番

`method.md` は何を決めて利益を計算するか、`experiment.md` は二つの例と画面の見方を説明します。`validation.md` では計算で確かめた範囲を示します。`implementation.md` は原式と実装上の注意、`mapping.md` は原論文との対応です。同じ文章を記事の各節にも表示します。

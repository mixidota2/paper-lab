# 品揃えを変えると、棚に必要な在庫はどう変わるか

この教材は、ある商品を外したとき、その商品を買うはずだった人の一部が別の商品へ移る場合を扱います。定期補充の間隔は固定し、移ってきた需要を含めて、どの商品を横に何列置けば必要な在庫を棚に入れられるかを調べます。入力は架空です。著者の実験、非公開データ、近似手順をそのまま再現したわけではありません。

## ページを開く

```bash
uv run --locked papers/assortment-replenishment-hard-constraints/run.py
uv run --locked --extra dev pytest tests/test_assortment_replenishment.py -q
uv run --locked python -m paper_lab.build --out /tmp/paper-lab-shelf-preview
uv run --locked python -m http.server 8000 --directory /tmp/paper-lab-shelf-preview
```

記事は /papers/assortment-replenishment-hard-constraints.html です。実験だけを開く場合は /downloads/assortment-replenishment-hard-constraints/interactive.html を使います。ダウンロードした実験を開くときは、model.js、interactive.js、results.jsonをinteractive.htmlと同じ場所に置き、HTTPサーバーから開いてください。Pythonの計算には標準ライブラリだけを使います。

## 4つの例で見ること

- T1：27候補のうち、棚幅に収まるのは10案で、棚在庫の条件も満たすのは7案です。条件を満たす案で最も高い利益は24です。代替を考えずに選んだ案は、移ってきた需要を足すと利益が21になりますが、必要な棚在庫を確保できません。
- T2：基準案と最適案は、どちらも条件を満たします。利益は基準案が10、最適案が16です。基準案は最適案より37.5%低く、この差は最適案の利益で割って求めます。
- T3：元の需要で条件を満たす最大利益は1です。需要を在庫に収まるように減らすと利益20という別の値が出ます。異なる条件で計算したため、二つの値を順位付けしません。
- T4：Bだけを採用すると、B自身の需要1個にAから移る4個が加わり、Bの需要は5個になります。

## 判定と検証の範囲

プログラムは、画面に丸めて表示した数値で可否を決めません。利益の同率判定には絶対差1e−9、棚幅の可否判定には絶対差1e−9、棚在庫の可否判定には1e−9×max(1,q,fD)の許容差を使います。最大利益が同じ案はすべて保存し、画面では面数の組を辞書順に並べて最初の案を表示します。

確認済み（CONFIRMED）は、この小規模な入力での計算照合を指します。原論文の仕組みは一部だけ検証しました（PARTIAL）。実店舗の性能、規模を大きくしたときの性能、本番への適用は検証していません（NOT TESTED）。著者コードは確認できていません（NOT OBSERVED）。

`tests/test_shelf_ui.py` は画面の表示分岐をブラウザーを使わず検査します。画面幅ごとの描画やダウンロードが実ブラウザーで動くことを、この検査だけで確認したとは扱いません。

## 記事と配布資料

`method.md` は需要と在庫の式、`experiment.md` は操作と4つの例、`validation.md` はどこまで検証したか、`implementation.md` は式と判定の実装を説明します。`mapping.md` には論文の式が実装のどこに対応するかをまとめました。

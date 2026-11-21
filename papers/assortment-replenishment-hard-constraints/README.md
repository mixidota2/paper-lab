# 品揃えと棚在庫の合成実験

補充間隔を固定したとき、商品を棚から外して移った需要に対し、残った商品の棚在庫を確保できるかを調べる教材です。採用する商品と横に並べる面数を選びます。独自の合成入力を使っており、原論文の実験・非公開データ・近似手順を完全に再現したものではありません。

```bash
uv run --locked papers/assortment-replenishment-hard-constraints/run.py
uv run --locked --extra dev pytest tests/test_assortment_replenishment.py -q
uv run --locked python -m paper_lab.build --out /tmp/paper-lab-shelf-preview
uv run --locked python -m http.server 8000 --directory /tmp/paper-lab-shelf-preview
```

/papers/assortment-replenishment-hard-constraints.html を開く。単体画面は /downloads/assortment-replenishment-hard-constraints/interactive.html。model.js、interactive.js、results.jsonを同じディレクトリに置き、HTTPで開く。Pythonは標準ライブラリのみ。

- T1：27候補のうち棚幅の条件を満たすのは10案、全条件を満たすのは7案です。採用品と面数を一緒に選んだときの最大利益は24です。代替なしで選んだ案は、移転分を足して再評価すると名目利益21ですが、在庫条件を満たさないため利益差の割合は出しません。
- T2：両案が条件を満たし、最適案の利益16に対して基準案は10です。差は最適利益を分母にして37.5%です。
- T3：元の需要で全条件を満たす最大利益1と、需要を切り詰めたときの利益20は、別の条件で計算した値です。
- T4：Bだけを採用すると、Bの需要は5になります。

確認済み（CONFIRMED）はこの小規模入力の計算照合。原論文の仕組みの確認は一部のみ（PARTIAL）。実店舗性能・規模・本番適用性、実ブラウザー操作と幅別表示は未検証（NOT TESTED）。著者コードは未確認（NOT OBSERVED）。

同率利益の許容差は絶対1e−9。在庫可否の判定に使う許容差は1e−9×max(1,q,fD)、幅の判定に使う許容差は絶対1e−9。表示丸めで判定しない。辞書順の代表と同率最適案を保存する。

図と操作文言の分岐は `uv run --locked --extra dev pytest tests/test_shelf_ui.py -q` で確認できる。DOMの代替を使ったソース検査であり、実ブラウザーの描画・画面幅・操作・ダウンロードの検証ではない。


## 本文の構成

`method.md` はモデルと仮定、`experiment.md` は合成例と操作、`validation.md` は教材の検証範囲、`implementation.md` は原式の補足と実装を説明します。共通ページの該当する節へ読み込みます。計算コード・入力・保存結果は本文の再構成では変更していません。

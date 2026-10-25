# 品揃えと棚在庫の合成実験

承認済み日本語原稿に沿い、固定補充周期の需要を棚在庫で受け止める条件を説明する。原論文の実験・非公開データ・近似手順の完全再現ではない。

```bash
uv run --locked papers/assortment-replenishment-hard-constraints/run.py
uv run --locked --extra dev pytest tests/test_assortment_replenishment.py -q
uv run --locked python -m paper_lab.build --out /tmp/paper-lab-shelf-preview
uv run --locked python -m http.server 8000 --directory /tmp/paper-lab-shelf-preview
```

/papers/assortment-replenishment-hard-constraints.html を開く。単体画面は /downloads/assortment-replenishment-hard-constraints/interactive.html。model.js、interactive.js、results.jsonを同じディレクトリに置き、HTTPで開く。Pythonは標準ライブラリのみ。

T1: 27候補、幅の条件を満たす案10、全条件を満たす案7、採用品と面数を一緒に選んだ最大利益24。代替なしで選んだ案を元の需要で再評価すると名目利益は21だが、在庫条件を満たさないため利益差の割合は定義しない。
T2: 16対10、最適値に対する不足率37.5%。T3: 元の全条件を満たす最大利益1と切詰め利益20は別問題。T4: Bだけ採用したとき需要5。

確認済み（CONFIRMED）はこの小規模入力の計算照合。原論文の仕組みの確認は一部のみ（PARTIAL）。実店舗性能・規模・本番適用性、実ブラウザー操作と幅別表示は未検証（NOT TESTED）。著者コードは未確認（NOT OBSERVED）。

同率利益の許容差は絶対1e−9。在庫可否は1e−9×max(1,q,fD)、幅は絶対1e−9。表示丸めで判定しない。辞書順の代表と同率最適案を保存する。

図と操作文言の分岐は `uv run --locked --extra dev pytest tests/test_shelf_ui.py -q` で確認できる。DOMの代替を使ったソース検査であり、実ブラウザーの描画・画面幅・操作・ダウンロードの検証ではない。


## 本文の構成

`method.md` はモデルと仮定、`experiment.md` は合成例と操作、`validation.md` は教材の検証範囲、`implementation.md` は原式の補足と実装を説明します。共通ページの該当する節へ読み込みます。計算コード・入力・保存結果は本文の再構成では変更していません。

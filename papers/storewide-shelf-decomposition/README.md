# 店全体の棚幅を配り、どの商品を何面置くか決める

買い物客に商品の正面を横に何列見せるかをフェイス数と呼びます。Labではカテゴリごとに幅別の最大利益を求め、それを使って店全体の棚幅を配ります。通路や棚の位置は決めません。

Tüzün Aksuほかの2025年論文（DOI 10.17341/gazimmfd.1600434）を、独自に作った6商品の例で読み解きます。利益は販売の粗利から補充費と商品採用費を引いたモデル値で、店舗で測った額ではありません。

## 計算と画面を再現する

リポジトリのルートで次を実行します。Pythonは標準ライブラリだけを使います。

```bash
uv run --locked papers/storewide-shelf-decomposition/run.py
uv run --locked --extra dev pytest tests/test_shelf_decomposition.py
uv run --locked python -m paper_lab.build --out /tmp/paper-lab-shelf-preview
```

既存の site/ は上書きせず、一時ディレクトリに全教材を生成します。run.py は乱数を使わず、同じディレクトリの results.json を更新します。画面を単独で試すときは interactive.html、interactive.js、model.js を同じディレクトリに置き、ローカルHTTPサーバーを使います。

```bash
uv run --locked python -m http.server 8000 --directory papers/storewide-shelf-decomposition
```

http://localhost:8000/interactive.html で、店全体の幅、代替率、面数による需要増、補充費、SKUの固定費、基礎需要を残す割合、最低ブランド数を変えられます。幅のボタンを押すと採用商品と費用が見えます。「現在の入力と結果を保存」で、合成入力と計算結果をJSONに保存できます。この改訂の実ブラウザーでの操作とスマートフォン・PCでの表示は未確認です。公開前に確認が必要です。

## 初期条件で選んだ案

店全体の幅をA:B=3:2に分け、A1を1面、A2とB1を2面ずつ置きます。A3、B2、B3は置きません。利益は150.78059291689343で、同じ利益の別のフェイス構成はありません。初期条件では基礎粗利に比例して幅を配る案も3:2ですが、この例だけで方式の優劣は判断できません。

Pythonは全店の729構成、JavaScriptはカテゴリごとの27構成を調べます。同点判定の絶対許容誤差は1e−9。表示する案はフェイス列の辞書順で決め、同じ列なら余分に割り当てる容量が少ない案を選びます。results.jsonには、一括列挙で求めた同利益のフェイス構成数を残します。割当幅が違うだけの案は別解に数えません。

## 何を確かめたか

- CONFIRMED：合成条件で直接需要を計算し、幅の候補をそろえた有限の探索で最適値が一致しました。検査は tests/test_shelf_decomposition.py にあります。
- PARTIAL：論文の仕組みと小規模例の対応を確認しました。線形化ソルバーと原論文規模の実験は再現していません。
- NOT OBSERVED：著者コードや継続中の商用運用を裏付ける独立資料は確認していません。
- NOT TESTED：実店舗の売上、利益、規模を広げた性能、本改訂の実ブラウザーでの表示・操作は未検証です。

教材の図、データ、コード、日本語の説明はLabの制作物で、原論文の全文や図版は転載していません。式と制約は method.md、印字の解釈と論文との対応は mapping.md にあります。

図や操作文の分岐は `uv run --locked --extra dev pytest tests/test_shelf_ui.py -q` で確認できます。この検査はDOMを代用し、実ブラウザーでの描画、幅、操作、ダウンロードは対象にしません。

## 各節を読む

`method.md` はモデルと仮定、`experiment.md` は合成例と画面の操作、`validation.md` は確認した範囲、`implementation.md` は原式の補足と実装を説明します。共通ページにも同じ説明を表示します。本文の再構成は計算、入力、保存結果の数値を変更しません。

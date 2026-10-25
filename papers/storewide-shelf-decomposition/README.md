# 棚を配る前に、各幅で何を売れるかを計算する

Tüzün Aksuほか（2025）、DOI 10.17341/gazimmfd.1600434を理解するための合成6 SKU実験。カテゴリ内の商品選択から価値表を作り、全店容量を配分する仕組みを動かす。今週の新刊という紹介ではない。

## 手元で実験を再実行する

リポジトリルートで実行する。Pythonは標準ライブラリだけを使用する。

```bash
uv run --locked papers/storewide-shelf-decomposition/run.py
uv run --locked --extra dev pytest tests/test_shelf_decomposition.py
uv run --locked python -m paper_lab.build --out /tmp/paper-lab-shelf-preview
```

ビルド先は一時ディレクトリに分け、全101件を生成する。既存のsite/は上書きしない。

`run.py`は同じディレクトリのresults.jsonを更新する。乱数は使わない。ブラウザー実験はinteractive.html、interactive.js、model.jsを同じディレクトリに保存し、ローカルHTTPサーバーで開く。

```bash
uv run --locked python -m http.server 8000 --directory papers/storewide-shelf-decomposition
```

http://localhost:8000/interactive.html を開く。全店容量、代替率、弾力性、補充費、SKU固定費、需要保持率、最低ブランド数を変更できる。価値表のボタンで採用SKUと費用の内訳を見る。「現在の入力と結果を保存」で合成入力と計算結果をJSONへ保存する。画面の実操作・スマホとPCの表示確認は未実施で、公開前の確認が必要。

## 初期値の答えを独立した全列挙で固定した

最適割当はA:B=3:2、フェイスはA1=1、A2=2、A3=0、B1=2、B2=B3=0。利益は150.78059291689343、別最適フェイス解はなく1通り。基礎粗利比例も初期値では3:2になる。この一致を方式の優劣の証拠にはしない。

Python側は6商品の729通りを一括列挙する。JavaScript側はカテゴリごとの27通りから価値表を作る。浮動小数点の同点許容誤差は1e−9。表示解はフェイス列の辞書順を優先し、不要な割当容量を最小にする。results.jsonには一括列挙側の別最適フェイス数も保存する。容量を変えても同じフェイスなら、別のフェイス解には数えない。

## 確認範囲を分ける

- CONFIRMED：合成条件での直接需要計算と有限候補内の最適値の照合。具体的な検査範囲はtests/test_shelf_decomposition.pyに記載。
- PARTIAL：原論文のメカニズム理解。線形化ソルバ・全規模計算は再現していない。
- NOT OBSERVED：著者の実装コード、継続中の商用運用を示す独立証拠。
- NOT TESTED：実店舗の売上・利益改善、性能と規模拡大、実ブラウザー画面。

図・データ・実装・日本語説明は本Labの自作。原典の全文や図版は複製していない。原典への対応と印字上の不整合はmapping.md、数式と制約はmethod.mdを参照。

図と操作文言の分岐は `uv run --locked --extra dev pytest tests/test_shelf_ui.py -q` で確認できる。DOMの代替を使ったソース検査であり、実ブラウザーの描画・画面幅・操作・ダウンロードの検証ではない。


## 本文の構成

`method.md` はモデルと仮定、`experiment.md` は合成例と操作、`validation.md` は教材の検証範囲、`implementation.md` は原式の補足と実装を説明します。共通ページの該当する節へ読み込みます。計算コード・入力・保存結果は本文の再構成では変更していません。

# 予測の順位は、何を合計してから測るかで変わる

対象は *World Models, Trees and Foundation Models for Retail Forecasting: Evidence from Four Public Data Sets*（arXiv 2610.25170v1）。Worth Reading。販促計画を読むモデル同士でも、商品別の予測誤差、カテゴリ別の費用、発注損失では選ぶモデルが変わり得ます。このLabはその評価手順を確かめる自作教材です。著者モデルの学習・推論や原実験を再現していません。

## 再実行

リポジトリの依存環境を用意したうえで、rootから実行します。

```sh
uv run python papers/retail-forecast-decision-grain/run.py
uv run pytest -q -ra --fail-on-skip tests/test_retail_grain.py
uv run python -m paper_lab.build --out /tmp/retail-grain-preview
```

公式CSVを別途取得済みの場合だけ、標準ライブラリの自作集計を実行できます。第三者コードを実行するコマンドではありません。

```sh
uv run python papers/retail-forecast-decision-grain/run.py --tables /path/to/official-csvs --out /tmp/table-counts.json
```

`category_cost.csv`の`variant=dollars`、`decisions.csv`の`set=rolling, decision=replenish_0.8`だけを採用します。category_planningは旧式なので使いません。結果は8パネルの最小値の件数であり、統計的優位の件数ではありません。第三者CSV・コード・PDFはこの配布物に同梱しません。

## 検証範囲

CONFIRMEDは自作の式の計算、境界値、保存結果との一致と公式CSVの限定集計です。MechanismはPARTIAL。原モデルの学習・推論、実店舗効果、運用費用はNOT TESTED。著者コードは読解のみで未実行です。学習済みモデルと著者の実行環境はNOT OBSERVEDです。DOM代用品のイベント検査は実ブラウザーの表示・操作確認ではありません。

UIは数値を0〜10000に制限し、空欄・負数・非有限数を拒否します。分母0は未定義と表示します。Pythonの一般計算は非負有理数を使い、返り値をJSON用数値へ変換します。図の横幅は親要素内に収め、操作欄は狭い幅では縦に並びます。実機の描画は未確認です。


CSV集計は入力ファイルのbytes・SHA256・Git blobを保存します。既知の2つのblobに両方一致した場合だけ`source_snapshot`を付け、未一致ならnullと`unverified_inputs`を返します。照合では完全一致と、保存時に末尾LFが1バイトだけ加わった一致を区別します。期待snapshotは照合基準であり、任意のCSVがそのsnapshot由来だと保証するものではありません。リポジトリ全体や原実験の再現を証明する照合でもありません。

## 比較条件を保存して読み直す

「現在の条件をJSON保存」で、集計単位・売上・予測・窓・発注量・不足費用比率と、現在の計算結果を保存できます。JSONは下の欄にも表示されます。保存したJSONを貼り付けて「JSONの条件を読み込む」を押すと、入力を検証してから条件を戻し、結果を再計算します。不正なJSONでは現在の条件を変更しません。

保存形式はschema 1、kindはretail-grain-scenario、model_versionはretail-grain-1です。synthetic=trueは自作合成例であることを示します。原著の予測や実験を再現したという意味ではありません。読み込み時は保存されたoutputを使わず、7項目のinputsから計算し直します。静的なresults.jsonや他のLabのJSONは、この条件保存形式ではありません。入力不正の間は保存を無効にし、初期値へ戻す操作では貼り付け欄も空にします。ファイルのダウンロードと貼り付けだけで動き、入力条件を外部へ送信しません。

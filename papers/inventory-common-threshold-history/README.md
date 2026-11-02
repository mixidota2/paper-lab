# 共通閾値と履歴を残す在庫判断

自作の小規模教材。論文の著者コード再現でも、店舗成果の再現でもありません。

```bash
uv run --locked python papers/inventory-common-threshold-history/run.py
uv run --locked pytest -q tests/test_inventory_ct.py
uv run --locked pytest -q -ra --fail-on-skip
uv run --locked python -m paper_lab.build
uv run --locked python tests/review_103.py --preflight --site site --out /tmp/inventory-preflight-new
```

最後の出力先は既存ディレクトリを指定しません。生成原本はresults.json、ページはsite/papers/inventory-common-threshold-history.html。静的初期表はビルド時に生成します。

3期間、4経路、需要合計最大3、信号2条件、納期0/1、固定ρ3値、履歴方式2条件で96経路表示。葉の確率は各1/4。乱数・Monte Carloは使いません。閾値分布の平均は、全履歴の時計が作る有限区間ごとにCDF差を掛けて計算します。実験の大きさを性能を見て増やしていません。

有限木は最大4期間・8葉・需要合計4まで受理します。有理数で確率・費用・時計を計算し、指数関数だけ浮動小数点にします。仕入費0、初期在庫0、容量制約なし。最適費用は履歴ごとに発注0〜残り最大需要を列挙するDPです。極端に大きい分数のビット長について資源保証はしません。

CONFIRMEDはこの有限例の自動検算・生成一致の範囲です。Mechanism全体はPARTIAL。著者コードはNOT OBSERVED。全証明、一般的な計算性能、実予測・実店舗適用、手動ブラウザーはNOT TESTED。一次本文のローカルbytes/hashは未取得で、Webによる読解を用いています。

JavaScriptは計算済み値の選択と描画だけを行います。自動テストは全条件、reset、no-JSとの対応を検査しますが、DOMの模擬検査を実ブラウザー操作とは呼びません。横長の計算表は表の領域内でスクロールします。

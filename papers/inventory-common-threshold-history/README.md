# 共通閾値と履歴を残す在庫判断

自作の小規模教材。論文の著者コード再現でも、店舗成果の再現でもありません。

```bash
uv run --locked python papers/inventory-common-threshold-history/run.py
uv run --locked pytest -q tests/test_inventory_ct.py
uv run --locked pytest -q -ra --fail-on-skip
uv run --locked python -m paper_lab.build
uv run --locked python tests/review_103.py --preflight --site site --out /tmp/inventory-preflight-new
```

最後のpreflightコマンドでは、検証記録を保存するために未使用のディレクトリを指定してください。計算結果はresults.jsonに保存され、ビルドするとsite/papers/inventory-common-threshold-history.htmlが生成されます。画面の初期表もビルド時に生成します。

3期間、4経路、需要合計最大3、信号2条件、納期0/1、固定ρ3値、履歴方式2条件で96経路表示。葉の確率は各1/4。乱数・Monte Carloは使いません。閾値分布の平均は、全履歴の時計が作る有限区間ごとにCDF差を掛けて計算します。実験の大きさを性能を見て増やしていません。

有限木は最大4期間・8葉・需要合計4まで受理します。有理数で確率・費用・時計を計算し、CDFの指数関数は精度50桁・ROUND_HALF_EVENのDecimalで評価してからfloatへ変換します。OSのlibmによる最下位桁の差を避け、保存JSONの厳密な再生成一致を保ちます。仕入費0、初期在庫0、容量制約なし。最適費用は履歴ごとに発注0〜残り最大需要を列挙し、将来の期待費用を遡って求める動的計画法（DP）で計算します。極端に大きい分数のビット長について資源保証はしません。

CONFIRMEDはこの有限例の自動検算・生成一致の範囲です。Mechanism全体はPARTIAL。著者コードはNOT OBSERVED。全証明、一般的な計算性能、実予測・実店舗適用、手動ブラウザーはNOT TESTED。一次本文のローカルbytes/hashは未取得で、Webによる読解を用いています。

JavaScriptは計算済み値の選択と描画だけを行います。自動テストは全条件、reset、no-JSとの対応を検査しますが、DOMの模擬検査を実ブラウザー操作とは呼びません。横長の計算表は表の領域内でスクロールします。


## `tight(epsilon)` の入力範囲

`epsilon` はまずPythonの`float`へ変換します。受理する範囲は `sys.float_info.min <= epsilon < 0.5` です。通常の64ビット浮動小数点では、下限は約2.225×10⁻³⁰⁸になります。正でもこの下限を下回る値は、費用を丸めたときの相対誤差が大きく、倍率を正しく表せないため、`ValueError`で拒否します。ゼロ、負数、0.5以上、NaN、無限大も受理しません。

CDFの計算では、小さい正の値に対して指数関数から1を引く桁落ちを避け、級数で直接計算します。画面の選択肢と保存済みの実験値は変わりません。CDFと期待費用の返り値は引き続き`float`です。この入力制限は`tight()`だけに適用し、任意の需要木で極小の期待費用を割り算した場合の相対精度までは保証しません。

CDFの内部計算は、呼び出し元のDecimalの桁数・丸め方・指数範囲・例外設定から切り離しています。呼び出し元の設定と計算状態も変更しません。

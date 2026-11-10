# 新しい系列を予測するとき、どの分割でモデルを選ぶか

対象は *Series-wise Cross-validation for Global Time Series Forecasting*（arXiv 2611.08252v1）。Worth Reading。既存系列の未来を予測するのか、学習に使わなかった系列も予測するのかで、モデル選択の評価対象が変わります。時間分割が常に誤りという論文ではありません。

このLabは10本×100点の合成系列による自作例です。ニューラルモデルや公式実装は実行しません。分割図、選択に使うラベル、予測時のcontext、重なる最終窓の重みを動かして確認します。公表Table3の丸め済み値による感度集計は、合成実験と別に表示します。

## 再実行と配布

repoの既存依存環境を使い、rootから実行します。出力先は既存資料を上書きしない専用の場所を指定してください。

```sh
uv run --locked python papers/series-wise-validation/run.py --out /tmp/series-cv-results.json
uv run --locked pytest -q -ra --fail-on-skip tests/test_series_cv.py
uv run --locked python -m paper_lab.build --out /tmp/series-cv-preview
```

保存JSONはoriginごとの予測・実績・誤差、contextと対象時点、選択結果、共通Qを含みます。UIのJSON保存では同じ合成結果と公表表の感度集計を別キーに分けます。原著の実行ログではありません。 ファイルを取得できない場合も、JSON保存ボタンを押すと同じ内容が画面の読み取り専用欄に表示されます。全内容をコピーして保存してください。条件変更・不正入力・初期化では、古い結果と混同しないよう欄を空にします。ダウンロードしたrun.pyには、同じディレクトリのtable3.jsonが必要です。

## 何を確認する教材か

CONFIRMEDは自作の時間境界、選択のtest非参照、Q=0の表示、丸め済み表の集計、保存結果の再生成の範囲です。原手法全体はPARTIAL。著者の学習済み重みと実行環境はNOT OBSERVED。原実験再現、実店舗・在庫費用・TSFM zero-shot性能、実ブラウザー描画はNOT TESTEDです。代用DOMやCSSの検査を実画面幅の確認とは呼びません。

Q=0ならMASEは未定義としてnullにし、MAEを併記します。欠損・非有限値は拒否します。この規則は教材独自で、原コードのQ=0処理を確認したものではありません。JSON保存とCLIは有限値だけを出力します。


## 計算入口の入力契約

`evaluate`が検証付きの主入口です。データはA〜Jだけをキーとする辞書／オブジェクトで、各系列は100個の値を持つPythonのlist／JavaScriptの密なArrayに限ります。数値文字列・真偽値・欠損・疎配列・非有限数は拒否します。値の範囲は−1,000,000〜1,000,000です。これはtoyの安全な計算範囲で、原著データの制約ではありません。

Qは自動計算、または0〜1,000,000の有限数です。UIの手入力範囲は従来どおり0〜100。Q=0のMASEはNone／nullですが、正のQが極端に小さく結果が非有限になる場合は例外です。NaNやInfinityをJSONのnullへ変えて正常値として返しません。

`fit`・`select`・`predict`・`scale_q`・`origins`・`role`は固定toyの内部・検査用で、任意入力向けのAPIではありません。検証済みデータとこの教材の系列・時間境界を前提にします。`sensitivity`も同梱Table3専用です。Pythonでは同梱JSONを読み、JavaScriptではそのJSON、掲載手法名、Weather包含の真偽値を内部から渡します。任意の表や欠損データへの汎用集計を保証しません。

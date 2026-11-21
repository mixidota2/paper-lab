# t0: A Time-Series Foundation Model for Forecasting with Context

著者は学習済みのt0-alphaを変えず、予測対象以外の変数（covariate）を入力する場合としない場合を比べた。fev-benchで予測時点に将来の値が分かる変数を使った30課題では、評価指標skillが36.7から43.0へ6.3ポイント上がった。改善したのは19課題で、残り11課題では悪化した。この比較からは、販促や欠品がある場合に時系列基盤モデル（TSFM）とGBDTのどちらが優れるかは分からない。

## 問い

同じモデルに、予測時点で分かっている予定を渡すと精度は上がるか

## 再実行

```bash
uv run papers/t0-tsfm-forecasting-with-context/run.py
```

Python標準ライブラリだけを使う。単体で取得した場合は `uv run run.py`。結果はスクリプトと同じ場所の `results.json` に保存する。

## 読む順序

`lab.yaml` で問題と根拠を確認し、`method.md` の仕組みと図へ進む。`run.py` と `results.json` で計算を追い、`mapping.md` で原論文や公式コードとの対応と省略点を確認できる。HTMLは `uv run paper-lab build` で生成する。

Mechanism PARTIAL。Performance / Scaling / Production applicability NOT TESTED。小実験で確認した局所条件のみCONFIRMEDとし、論文の本番数値を再現したとは扱わない。

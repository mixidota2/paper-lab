# t0: A Time-Series Foundation Model for Forecasting with Context

t0-alphaの同一checkpointでcovariateを入切すると、fev-benchの既知未来30課題でskill 36.7→43.0、+6.3ポイント。19課題は改善し11課題は悪化。販促・欠品条件でTSFMとGBDTを比較した結論ではない。

## 問い

同じ予測モデルに、未来の予定を渡す価値はあるか

## 再実行

```bash
uv run papers/t0-tsfm-forecasting-with-context/run.py
```

Python標準ライブラリだけを使う。単体で取得した場合は `uv run run.py`。結果はスクリプトと同じ場所の `results.json` に保存する。

## 読む順序

`lab.yaml` の問題設定・根拠、`method.md` の仕組みと図、`run.py` と `results.json`、`mapping.md` の省略点。HTMLは `uv run paper-lab build` で生成する。

Mechanism PARTIAL。Performance / Scaling / Production applicability NOT TESTED。小実験で確認した局所条件のみCONFIRMEDとし、論文の本番数値を再現したとは扱わない。

# t0: A Time-Series Foundation Model for Forecasting with Context

The Forecasting Companyの研究チームは、学習済みの時系列モデルt0-alphaに、売上や価格の履歴だけでなく、販促や祝日などの情報を渡すと予測が改善するかを調べました。モデルの重みは固定し、同じモデルに追加情報を渡す場合と渡さない場合を比べました。ここで紹介するのはt0-alphaの結果で、後継のt0-betaとの性能比較ではありません。

将来の予定や予報を使える30課題では、季節のパターンを繰り返す基準に比べ、予測誤差がどれだけ小さいかを表す指標（skill）が36.7から43.0へ、6.3ポイント上がりました。30課題のうち改善したのは19課題で、残り11課題は悪化しました。Rossmannの売上データでは販促、祝日、営業日を追加すると分位点の予測誤差が43%減りましたが、M5の週次と月次では改善も悪化も2%未満でした。6.3ポイントは30課題をまとめた指標の差で、平均絶対誤差（MAE）が6.3%減ったという意味ではありません。

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

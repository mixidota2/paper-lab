# Beyond Raw Engagement: A Counterfactual Observability Framework for Recommender Systems at Netflix

NetflixのCONSEQUENCES論文は、推薦の成果を「その作品や判断がなかった場合との差」で測る。行の増分価値は11件の除去A/BとR²=0.8212。新しいrankerではなく、engagement liftの読み方と障害の見つけ方を変える。

## 問い

よく見られた作品は、なくなると困る作品なのか

## 再実行

```bash
uv run papers/netflix-counterfactual-observability/run.py
```

Python標準ライブラリだけを使う。単体で取得した場合は `uv run run.py`。結果はスクリプトと同じ場所の `results.json` に保存する。

## 読む順序

`lab.yaml` の問題設定・根拠、`method.md` の仕組みと図、`run.py` と `results.json`、`mapping.md` の省略点。HTMLは `uv run paper-lab build` で生成する。

Mechanism PARTIAL。Performance / Scaling / Production applicability NOT TESTED。小実験で確認した局所条件のみCONFIRMEDとし、論文の本番数値を再現したとは扱わない。

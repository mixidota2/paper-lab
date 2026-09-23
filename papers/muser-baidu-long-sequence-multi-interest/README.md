# MuSeR: Scalable Long-sequence Recommendation with Multi-interest Modeling

MuSeRはBaiduのretrievalに、時間別の履歴圧縮・6つのinterest query・意味表現・非同期cacheを統合する。homepageの同一A/BでDAU +0.26%、session duration +0.89%。圧縮は非圧縮のrecallを完全には保たない。

## 問い

昔の履歴を粗く残し、複数の関心を配信時間内に使えるか

## 再実行

```bash
uv run papers/muser-baidu-long-sequence-multi-interest/run.py
```

Python標準ライブラリだけを使う。単体で取得した場合は `uv run run.py`。結果はスクリプトと同じ場所の `results.json` に保存する。

## 読む順序

`lab.yaml` の問題設定・根拠、`method.md` の仕組みと図、`run.py` と `results.json`、`mapping.md` の省略点。HTMLは `uv run paper-lab build` で生成する。

Mechanism PARTIAL。Performance / Scaling / Production applicability NOT TESTED。小実験で確認した局所条件のみCONFIRMEDとし、論文の本番数値を再現したとは扱わない。

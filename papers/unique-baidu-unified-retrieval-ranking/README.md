# UNIQUE: A Unified Retrieval and Ranking System for Large-Scale Feed Recommendation

Baidu/BeihangのUNIQUEはflatな意味codeと候補ごとのtarget attentionを共有モデルへ統合する。Mobile Baiduの1週間A/Bでwatch duration +0.96%、distribution volume +1.08%。P99 89 msはretrieval serviceの条件付き実測。

## 問い

候補生成と順位付けは、どの表現まで共有できるか

## 再実行

```bash
uv run papers/unique-baidu-unified-retrieval-ranking/run.py
```

Python標準ライブラリだけを使う。単体で取得した場合は `uv run run.py`。結果はスクリプトと同じ場所の `results.json` に保存する。

## 読む順序

`lab.yaml` の問題設定・根拠、`method.md` の仕組みと図、`run.py` と `results.json`、`mapping.md` の省略点。HTMLは `uv run paper-lab build` で生成する。

Mechanism PARTIAL。Performance / Scaling / Production applicability NOT TESTED。小実験で確認した局所条件のみCONFIRMEDとし、論文の本番数値を再現したとは扱わない。

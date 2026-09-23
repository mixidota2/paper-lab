# HGenPush: A Heterogeneous Generative Recommendation Architecture for Industrial Push Notification Systems

KuaishouのHGenPushはvideo SIDとauthor中心のmixed SIDを生成し、pre-rankを迂回して既存rankerへ渡す。全構成のDAU +0.181%（p=0.04）、CTR +1.577%（p=0.11）。CTRの有意差は確認できない。

## 問い

動画と作者の二つの経路を、同じpush候補へつなげられるか

## 再実行

```bash
uv run papers/hgenpush-kuaishou-heterogeneous-push-gr/run.py
```

Python標準ライブラリだけを使う。単体で取得した場合は `uv run run.py`。結果はスクリプトと同じ場所の `results.json` に保存する。

## 読む順序

`lab.yaml` の問題設定・根拠、`method.md` の仕組みと図、`run.py` と `results.json`、`mapping.md` の省略点。HTMLは `uv run paper-lab build` で生成する。

Mechanism PARTIAL。Performance / Scaling / Production applicability NOT TESTED。小実験で確認した局所条件のみCONFIRMEDとし、論文の本番数値を再現したとは扱わない。

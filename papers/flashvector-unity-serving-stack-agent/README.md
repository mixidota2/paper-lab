# FlashVector: Agent for Hierarchical Model Serving Stack Optimization

著者は、モデルの配信が遅いときに、GPUの計算だけでなく、入力の変換や特徴量の組み立ても調べるエージェントを開発しました。FlashVectorは時間がかかっている箇所を測り、コードや設定の変更を提案します。変更後も同じ出力になるか、応答時間やシステム全体の処理件数がどう変わるかを調べ、その結果を採用の判断に使います。

同じ環境で比べた事例では、著者はある順位付けモデルの処理件数が同じ時間で2.00倍になったと報告しました。一方、候補検索モデルで30倍になったのは入力変換の処理であり、配信システム全体の処理件数は1.10倍でした。これらは個別のモデルで測った値で、全モデルの平均や、広告のクリック率の改善を示すものではありません。

## 問い

kernelが速くなっても、配信全体が速くならなければ棄却できるか

## 再実行

```bash
uv run papers/flashvector-unity-serving-stack-agent/run.py
```

Python標準ライブラリだけを使う。単体で取得した場合は `uv run run.py`。結果はスクリプトと同じ場所の `results.json` に保存する。

## 読む順序

`lab.yaml` の問題設定・根拠、`method.md` の仕組みと図、`run.py` と `results.json`、`mapping.md` の省略点。HTMLは `uv run paper-lab build` で生成する。

Mechanism PARTIAL。Performance / Scaling / Production applicability NOT TESTED。小実験で確認した局所条件のみCONFIRMEDとし、論文の本番数値を再現したとは扱わない。

# RecEvolve: A Knowledge-Driven Autonomous Agent System for Recommender Systems

GoogleのRecEvolveは、本番Two-Tower検索モデルの仮説・批評・実装・学習・評価をOrchestratorでつなぐ。著者報告は41実験、最終NDCG@50が0.4796から0.5751、オンライン満足度+3.77%。同時に、batchを8kから1kへ減らすと評価だけが易しくなる問題も発見された。KEEPとVCS rollbackの条件、評価候補の固定を中心に読む。

## 実行

```bash
uv run papers/recevolve-autonomous-rec/run.py
uv run paper-lab build
```

Python標準ライブラリだけで動く。実行場所に依存せず、同じフォルダーの `results.json` を更新する。

## 原本

`lab.yaml` が本文・図の定義、`method.md` が手法、`mapping.md` が原論文との対応。HTMLはgeneratorで生成する。`run.py` と `results.json` が合成実験の原本。

## 検証範囲

Mechanism PARTIAL、Performance / Scaling / Production applicability NOT TESTED。CONFIRMEDはJSONに記した個別の算術・比較条件だけを指す。論文のモデルを訓練した結果ではない。

[一次資料・全文](https://arxiv.org/html/2609.01622v1)。確認日：2026-09-15。詳細な未検証項目と出典上の注意はLab本文・mappingを参照。

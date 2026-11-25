# RecEvolve: A Knowledge-Driven Autonomous Agent System for Recommender Systems

GoogleのRecEvolveは、本番で使う動画推薦の候補検索モデルを改良するため、仮説を出す、検討する、実装する、学習して評価するという作業をつなぎます。対象は利用者側と動画側で別々に特徴を計算する二塔型モデルです。評価が基準を満たす変更は残し、満たさない変更は元に戻します。

著者は41件の実験を行い、複数の変更を積み重ねた最終構成で、オフラインの上位50件の順位の指標（NDCG@50）が0.4796から0.5751に上がったと報告しました。本番のA/Bテストでは、満足度の指標が従来モデルより3.77%増えています。別の試行ではモデルが良くなったのではなく、評価条件が変わったために数値が上がったと判明しました。この試行は元に戻し、最終構成の改善とは区別しています。

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

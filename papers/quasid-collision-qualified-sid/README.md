# Stop Treating Collisions Equally: Qualification-Aware Semantic ID Learning for Recommendation at Industrial Scale

QuaSIDは、SIDの重なりから反発対象を選ぶ学習法である。同一itemと協調正例をmaskで除き、完全衝突と部分衝突に異なる幾何マージンを課す。KuaishouはrankingのGMV-S2 +2.38%、cold-start retrievalの注文数+6.42%を報告する。衝突ゼロの保証と、害のある衝突を減らす学習を区別する。

## 実行

```bash
uv run papers/quasid-collision-qualified-sid/run.py
uv run paper-lab build
```

Python標準ライブラリだけで動く。実行場所に依存せず、同じフォルダーの `results.json` を更新する。

## 原本

`lab.yaml` が本文・図の定義、`method.md` が手法、`mapping.md` が原論文との対応。HTMLはgeneratorで生成する。`run.py` と `results.json` が合成実験の原本。

## 検証範囲

Mechanism PARTIAL、Performance / Scaling / Production applicability NOT TESTED。CONFIRMEDはJSONに記した個別の算術・比較条件だけを指す。論文のモデルを訓練した結果ではない。

[一次資料・全文](https://arxiv.org/html/2603.00632v1)。確認日：2026-09-15。詳細な未検証項目と出典上の注意はLab本文・mappingを参照。

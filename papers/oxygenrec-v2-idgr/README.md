# OxygenREC-v2: Internalizing Discrimination into Generative Recommendation

JD.comのOxygenREC-v2は、click・cart・orderの指示でSID生成を条件付ける。学習時には実ログとの一致と、未来行動を見た同一backboneの教師を使う。IDGRの焦点は行動信号を入れる位置にある。6つの配信面のA/Bを読み分け、外部報酬モデルの除去をサービス全体のカスケード撤去へ広げない。

## 実行

```bash
uv run papers/oxygenrec-v2-idgr/run.py
uv run paper-lab build
```

Python標準ライブラリだけで動く。実行場所に依存せず、同じフォルダーの `results.json` を更新する。

## 原本

`lab.yaml` が本文・図の定義、`method.md` が手法、`mapping.md` が原論文との対応。HTMLはgeneratorで生成する。`run.py` と `results.json` が合成実験の原本。

## 検証範囲

Mechanism PARTIAL、Performance / Scaling / Production applicability NOT TESTED。CONFIRMEDはJSONに記した個別の算術・比較条件だけを指す。論文のモデルを訓練した結果ではない。

[一次資料・全文](https://arxiv.org/html/2607.24255v1)。確認日：2026-09-15。詳細な未検証項目と出典上の注意はLab本文・mappingを参照。

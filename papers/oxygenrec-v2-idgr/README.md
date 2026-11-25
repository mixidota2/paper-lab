# OxygenREC-v2: Internalizing Discrimination into Generative Recommendation

JD.comのOxygenREC-v2では、クリック、カートへの追加、注文のどれを狙うかを最初に指定します。その条件で商品の特徴を表すコード（SID）を生成するため、同じ利用者でも、注文を狙うときはクリックを狙うときと異なる候補を出せます。追加学習に使うのは、生成結果と記録された行動が一致したかどうかと、後に起きた行動まで見られる同じモデルからの予測です。配信時には将来の行動を入力しません。

著者はJD.comの6つの配信面で、それぞれ従来の本番モデルと比較しました。追加学習前の変更を試したホーム画面とチャンネルの一覧では、クリック後の転換率（UCTCVR）が1.61〜4.44%増加。追加学習の変更を試した商品詳細画面では、取引総額（GMV）が4.25%増えました。外部の報酬モデルを使わずに学習したという結果で、配信全体から他の推薦処理を取り除いたという意味ではありません。

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

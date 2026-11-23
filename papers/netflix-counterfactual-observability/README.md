# Beyond Raw Engagement: A Counterfactual Observability Framework for Recommender Systems at Netflix

よく見られた作品でも、代わりに出した作品が同じように見られるなら、その作品を外す損失は小さくなります。NetflixのCONSEQUENCES論文は、推薦の成果が「その作品や判断がなかった場合」と比べてどう変わるかを調べます。ホーム画面の行を取り除いたときに失われる価値の推定値を、行を実際に除去した11件のA/Bテストと比べると、決定係数R²は0.8212でした。新しく作品を並べる手法ではなく、推薦によって増えた視聴などをどう読み、障害の原因をどう見つけるかを扱います。

## 問い

よく見られた作品は、なくなると困る作品なのか

## 再実行

```bash
uv run papers/netflix-counterfactual-observability/run.py
```

Python標準ライブラリだけを使います。ファイルを単体で取得した場合は `uv run run.py` を実行してください。結果はスクリプトと同じ場所の `results.json` に保存します。

## 読む順序

まず `lab.yaml` で問いと根拠を確認し、次に `method.md` で仕組みと図を読みます。計算と出力は `run.py` と `results.json`、原論文から省いた部分は `mapping.md` にあります。HTMLを生成するには `uv run paper-lab build` を実行します。

仕組みは一部確認済み（Mechanism PARTIAL）です。性能、規模を広げたときの挙動、本番に使えるかどうか（Performance / Scaling / Production applicability）は未検証（NOT TESTED）です。確認済み（CONFIRMED）とするのは小実験で実際に確認した条件だけで、論文の本番数値を再現したわけではありません。

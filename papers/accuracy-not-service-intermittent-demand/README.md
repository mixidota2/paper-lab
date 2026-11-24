# 予測誤差が小さいモデルが、注文を最も多く完納するとは限らない

[原論文：Accuracy Is Not Service](https://arxiv.org/abs/2609.13840)

部品の実注文20,330件を同じ補充規則で処理した著者の比較では、38手法の予測誤差と完納率の順位相関は−0.555だった。別の実験で、著者がChronos-2の入力の正規化を変えると、誤差は悪化したが完納率は54%から63%に上がった。発注に使う手法は誤差だけでなく、同じ条件での完納率と在庫費用も見て選ぶ。

[Labで解説と図を読む](https://mixidota2.github.io/paper-lab/papers/accuracy-not-service-intermittent-demand.html)

## Labの人工注文を再実行する

```bash
uv run papers/accuracy-not-service-intermittent-demand/run.py
```

`run.py` が人工注文の処理と正規化の計算を行い、`results.json` に結果を保存する。Python標準ライブラリだけで動く。画面の説明は `lab.yaml` と `method.md`、論文とLabの対応は `mapping.md` にある。リポジトリの最上位で `uv run paper-lab build` を実行するとHTMLを作れる。

## 確認したことと、確認していないこと

仕組みは一部を確認した（PARTIAL）。人工データで、正規化した値を元に戻せること、入力がすべてゼロでも有限の値を返すこと、補充規則に沿って在庫と完納を計算できることを確かめた。在庫を増やすと完納率が下がる3注文の例も確認した（この条件ではCONFIRMED）。144件の人工注文では、論文と同じ順位の逆転は見られなかった（NOT OBSERVED）。

予測性能、大規模データでの動作、本番への適用は未検証（NOT TESTED）。LabはChronos-2の学習済みモデルを使っていないため、正規化を変えた後の予測は調べていない。非公開注文の処理、RUFの生成、38手法の学習、信頼区間の推定、在庫金額の最適化も行っていない。公開CSVから求め直したのは著者が報告した順位の相関である。

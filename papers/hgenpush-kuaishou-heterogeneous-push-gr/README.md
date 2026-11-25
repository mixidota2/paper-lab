# HGenPush: A Heterogeneous Generative Recommendation Architecture for Industrial Push Notification Systems

KuaishouのHGenPushは通知で届ける動画の候補を二つの経路で探します。動画から探す経路は、動画の特徴を3段階で表したコード（SID）を生成します。投稿者から探す経路が生成するのは、利用者が好みそうな投稿者を表す2段階のコードと、動画の特徴を表す最初のコードの組み合わせです。この経路の目的も、投稿者を通知することではなく、その投稿者の動画を探すことです。

両方の経路から得た候補は、予備の順位付けを経ずに、最終的な順位を決めるモデルへ渡ります。著者が従来の通知システムと比較したA/Bテストでは、両経路を使う構成で1日あたりのアクティブ利用者数が0.181%増えました。同じ構成では、通知のクリック率とアプリ利用時間の差は5%水準で統計的に有意ではありませんでした。

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

# MuSeR: Scalable Long-sequence Recommendation with Multi-interest Modeling

BaiduのMuSeRは古い履歴を期間ごとに異なる粒度でまとめ、6つのinterest queryで利用者の異なる関心を取り出す推薦候補検索の方式だ。意味表現と非同期キャッシュも組み合わせる。ホームページでの同じA/Bテストで、DAUは0.26%、セッション時間は0.89%増えた。一方、履歴を圧縮すると、圧縮しない場合と同じ候補回収率（recall）を完全には保てない。

## 昔の履歴をどこまで残せるか

古い履歴を粗く残し、配信に使える時間内に、利用者が持つ複数の関心を利用できるかを考える。

## 教材の計算を実行する

```bash
uv run papers/muser-baidu-long-sequence-multi-interest/run.py
```

Python標準ライブラリだけを使う。教材を単体で取得した場合は `uv run run.py` を実行する。結果はスクリプトと同じ場所の `results.json` に保存する。

## 各ファイルで確認できること

最初に `lab.yaml` で問題設定と根拠を確認し、`method.md` の説明と図を読む。次に `run.py` と `results.json` を照らし合わせ、最後に `mapping.md` で原論文との対応と省略した箇所を確認する。HTMLは `uv run paper-lab build` で生成する。

仕組みの確認は一部に限る（Mechanism: PARTIAL）。性能、規模を拡大したときの挙動、実運用への適用は検証していない（Performance / Scaling / Production applicability: NOT TESTED）。確認済み（CONFIRMED）とするのは小実験で確かめた局所的な条件に限り、論文の本番数値を再現したわけではない。

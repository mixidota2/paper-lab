# Unifying Generative Recall and Multi-Objective Ranking in a Single Decoder-Only Sequence

Kuaishouの研究チームは、ライブ配信の候補を探す処理と、最終順位付けの前に候補を絞る処理を、一つのTransformerにまとめました。UniR²は利用者の文脈を読み、候補を表すIDの列を生成します。同じモデルはその途中の情報と候補の特徴を使い、候補を絞るための点数を計算します。

著者は2026年6月に、配信の5%を使って従来のOneLiveによる候補検索と予備順位付けを置き換え、2週間比較しました。Kuaishou本体では再生回数が1.177%増え、Kuaishou Liteではギフト総額が2.569%増えました。異なるアプリの指標であり、推薦の全段階を置き換えた結果でもありません。

`uv run papers/unir2-sequence-unify/run.py`

本文の原データは lab.yaml と method.md、対応表は mapping.md。run.py は標準ライブラリのみを使い、results.json を同じディレクトリに生成する。数値は合成例で、論文の再現実験ではない。

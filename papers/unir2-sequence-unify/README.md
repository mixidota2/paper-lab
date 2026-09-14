# Unifying Generative Recall and Multi-Objective Ranking in a Single Decoder-Only Sequence

UniR²はユーザー文脈、SID軌跡、item featuresを一つのdecoder系列へ置く。Kuaishouの2週間・5% A/BではOneLive recallと本番pre-rankを同時に置換した。全カスケードの撤去とは区別し、可視範囲・勾配・KV再利用の境界を読む。

`uv run papers/unir2-sequence-unify/run.py`

本文の原データは lab.yaml と method.md、対応表は mapping.md。run.py は標準ライブラリのみを使い、results.json を同じディレクトリに生成する。数値は合成例で、論文の再現実験ではない。

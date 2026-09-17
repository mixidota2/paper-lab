# Generative Recommendation for Large-Scale Advertising

GR4ADは広告SID、価値に沿う学習、短い系列の復号、負荷に応じたbeam幅を合わせて設計する。Table 1の最終構成は収益+4.28%（対DLRM）、QPS+117%（対OneRec-V2）。比較基準を分けて、400M超ユーザーへの展開という著者報告を読む。

`uv run papers/gr4ad-ads-generative/run.py`

本文の原データは lab.yaml と method.md、対応表は mapping.md。run.py は標準ライブラリのみを使い、results.json を同じディレクトリに生成する。数値は合成例で、論文の再現実験ではない。

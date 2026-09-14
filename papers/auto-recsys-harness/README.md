# Auto-RecSys: Harnessing Autonomous Research Agents for Industry-Scale Recommender Systems

Auto-RecSysは数日単位の推薦実験を非同期に進め、実行手順と研究上の知見を別のループで蓄積する。1モデル31反復の運用修正は平均4.0→1.3、baseline更新を挟んで0.5へ低下した。主な根拠は運用ログであり、学習時間や推薦性能の改善実験ではない。

`uv run papers/auto-recsys-harness/run.py`

本文の原データは lab.yaml と method.md、対応表は mapping.md。run.py は標準ライブラリのみを使い、results.json を同じディレクトリに生成する。数値は合成例で、論文の再現実験ではない。

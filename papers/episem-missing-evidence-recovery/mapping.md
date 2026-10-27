# 原典と自作実装の対応

| 原典 | Lab | 一致させた条件と省略 |
|---|---|---|
| §3.1、Fig 1 | run.py の TASKS / pair、model.js の tasks / pair | 同一request・schemaの禁止/許可双子。2種類の自作規則に簡略化。著者の300対ではない |
| §3.2 | rollout の hidden / visible / read_again | 全ての通常観測で欠落を維持。criticalとirrelevantを別指定。実ツールの複雑な露出経路は省略 |
| §3.3、Appendix E | audit / audit_not_executed | REの有効auditだけが全欠落を正しい値で返す。commit後は実行不可。toyでは最終停止も終端にする |
| §3.4、式(1)、Appendix B | boundary / metrics | baseline失敗は0、最小欠落数、全列挙後だけc+1。toyの集計は全mask固定coverage。著者のhash探索順序は再現しない |
| §3.4、式(2) | pair.paired / metrics.pur | 同一非空critical maskの両世界で厳密回収が必要。task内平均→task等重み |
| Table 1、Appendix C.2 | evidence.md、results.json の reported | 最小限の著者報告値。syntheticと分離。順位を推奨しない |

Pythonが参照結果を生成し、JavaScriptはブラウザーで同じ小さな規則を実行する。全480条件と全方策の集計を比較する。ブラウザーでの操作テストと、モデル性能の検証は別である。ネットワーク呼出し・認証・課金・実送信は実装しない。

[Qijin Zhangほか、EpiSEM-Bench、arXiv 2610.31650v1](https://arxiv.org/abs/2610.31650v1)、2026年10月22日。原典のライセンス表示はarXiv perpetual non-exclusive license。CC BYとは扱わず、図版・本文の大量転載をしない。説明、toy、操作画面は独自制作。公式コードの対応関数はNOT OBSERVED。

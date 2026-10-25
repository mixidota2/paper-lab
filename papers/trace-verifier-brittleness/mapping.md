| 原典 | Labの対応 | 境界 |
|---|---|---|
| §2 / Fig 1 | 対応実行→点差→行動確認→固定記録の再採点 | 図版を転載せず、自作例で説明 |
| §3.1 / Fig 2 | run.py rollout, score(normalize=True) | 別名で同じ正規操作、採点時だけ正規化。原論文の0.250を再現していない |
| §3.2 / Table 2 | weakスクリプト、安定性の表 | 一貫した失敗でも差は小さい。数字は自作例 |
| §2.2 | VRG・MSR・MTRの説明 | VRGとTable 6のΔは符号が逆。MTRの分母ゼロは未定義 |
| §5 / Appendix E Table 6 | evidence.md、results.json.reported | 88×3と158×2、90%と95%を区別。Qwen formatはinconclusive |
| §5 / Appendix E Table 8 | 判定一致と正確性の区別 | 118本の固定軌跡。native rewardを真実ラベルとみなさない |
| 公開コード | READMEとツリーを読み取り確認 | public-trace-agentic-ai-summit、4e42d6a70832eeb0c2a2caa0062524ef0559995e。Study 2/3再計算は未実施 |
| 自作の実験 | run.py → results.json.synthetic / experiment.md | 決定的な在庫修正。名前を除いた操作列と状態のSHA-256を比較 |

一次資料：[本文v1](https://arxiv.org/html/2610.11678v1)、[PDF v1](https://arxiv.org/pdf/2610.11678v1)、[公式コードの確認版](https://github.com/RGaonkar/trace-verifier-stress-tests/tree/4e42d6a70832eeb0c2a2caa0062524ef0559995e)。本文の確認日は2026-10-15。公開コードのcommit日時は2026-08-02T05:41:14Zで、READMEと保存パスはposter/syntheticと7月28日の164タスク診断を示す。本文の全結果との対応は確認できない。

意図して省いたもの：ResearchOpsの25課題、Appendix Aの複合採点器、LLMの対話生成、τ²-benchの環境、bootstrap、positive controlの再実行、学習ループ。モデルの正確性・判定器の正確性は検証していない。

原論文のライセンスはCC BY-NC-SA 4.0。図版・コードをコピーせず、自作例で概念を説明した。公開報告値は出典付きで記載し、独立再現値と混ぜない。

書誌情報：[arXiv登録ページ](https://arxiv.org/abs/2610.11678)。v1の公開日時は2026-10-08 10:52:26 UTC。

| 原論文の場所 | Labの対応 | 範囲と留保 |
| --- | --- | --- |
| Figures 1–2、§3 | Orchestrator lifecycle図 | agent役割と状態の保持先を再構成 |
| 式1–2 | モデル探索の定式化 | 学習済みpolicyをLabで訓練しない |
| Algorithm 1 | `decide()` / `lifecycle()` | in-memory状態。VCSの実行なし |
| §5.2 | `candidate_probe()` | score固定。8k→1kの難易度差だけ |
| Table 1、Figure 3 | 累積構成のtrajectory | 表で公開された4点のみ |
| Table 2、§5.7 | online指標の読解 | Cold-startは発見時間の短縮 |

[全文v1](https://arxiv.org/html/2609.01622v1)を§1–7とReferencesまで通読。公開HTMLには独立した付録はない。arXiv書誌のSubmittedは2026-07-20と表示されるため、その日付を採用した（IDの月から推測しない）。公式コードは本文・書誌で未確認。引用されるautoresearchはRecEvolve自身の公開実装ではない。

候補数不変の監査はLab独自。原論文の人間による検出を、Orchestratorが自動で発見した成果として扱わない。

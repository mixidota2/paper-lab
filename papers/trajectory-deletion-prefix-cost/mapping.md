| 原典 | このLab | 境界 |
|---|---|---|
| §II-C・Fig. 1・§III-C | run.py の lcp / ledger、トークン帯 | 完全一致する接頭辞と費用だけを実装。実KVキャッシュではない |
| §III-B | method.md の削除範囲・時点 | toyは1回の決定的削除。著者の確率的な全構成を再現しない |
| Tables I–III・§VI | evidence.md、results.reported | 著者報告。生ログからの再計算ではない |
| §III-D・VII | 不確実性と限界 | 課題bootstrapと介入再実行の変動を区別 |
| §VIII | 関連研究の説明 | AgentDiet、Token Reduction Is Not Cost Reduction、interaction-cost研究を先行研究として扱う |

一次資料：[The Hidden Costs of Forgetting, arXiv 2610.35496v1](https://arxiv.org/html/2610.35496v1)、2026-10-26。Fernando Vallecillos-Ruiz, Islem Bouzenia, Michael Pradel, Leon Moonen。本文のライセンス表示はCC BY 4.0。図と説明文はこのLabで新しく制作した。

本文§I–IXとTables I–IIIをHTMLで確認。公式Figshare packageはNOT OBSERVED。過去の取得失敗後に再試行しておらず、軌跡・公式分析コードを読んだ／動かしたとはしない。

既存の[外部状態と忘却のLab](agent-reasoning-forgetting-externalized-state.html)は、状態を回収できる条件を扱う。本Labは再送する入力の完全一致と費用を分離する。仕組みの初発見という評価はしない。

書誌：[arXiv abstract](https://arxiv.org/abs/2610.35496)。

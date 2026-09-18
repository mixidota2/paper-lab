# PILOT Technical Report

PILOTはExperiment Manager・Search Planner・Memory Curatorを、決定的な安全・統計・権限の境界で囲む。Taobaoの前後比較でbest-bucket IPVはROAM +1.00%に対し+1.40%、探索条件の達成率は53.3%から93.3%。設計は具体的だが、Manager×Plannerの2×2比較は未実施なのでWatchとする。

## 読み方

PILOT：提案するagentから、実験を運営するagentへ。まず問題設定と手法を読み、図で操作の単位を追う。Evidenceでは比較の分母と観察範囲を確認し、小実験と原論文の性能を分けて評価する。

著者は、Managerによる能動的な実験運営、Plannerによるsegment別探索、Curatorによる経験蓄積が、反応的なROAMより探索の進捗を増やすと主張する。

【Labの解釈】決定的なサービスが判断可能な選択肢を先に限定する設計に注目したい。within-taskの有意性とcross-taskの記憶の確信度を分ける設計は再利用しやすい。一方、比較実験はその設計の個別寄与まで裏づけていない。

## 再実行

```bash
uv run papers/pilot-experiment-lifecycle/run.py
uv run paper-lab build
```

lab.yaml、method.md、mapping.md、run.py、results.jsonが原本。site/は生成物であり直接編集しない。実験は標準ライブラリのみ。

## 検証範囲

**Mechanism: PARTIAL**。人工条件の計算と境界条件を確認した。results.jsonのCONFIRMEDは小さな計算命題にだけ適用する。原論文の学習済みモデルや産業環境を再現した意味ではない。

LLMの候補品質、逐次検定、多重比較補正、sample ratio mismatch検出、実trafficの承認workflow、PolicyTreeの5 action全実装、memoryの自動反証統合は未検証。人工guardが動くことからIPV改善や自律実験の安全性は導けない。

Performance / Scaling / Production applicability: NOT TESTED。モデル学習とオンラインA/Bは実行していない。

[一次PDF](https://arxiv.org/pdf/2608.18637v1)。版・ハッシュ・節とコードの対応はmapping.md。公式コードは確認範囲で案内を見つけられず、実行していない。

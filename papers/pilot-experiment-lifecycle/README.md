# PILOT Technical Report

TaobaoのPILOTは推薦設定の実験を三つの役に分ける仕組みです。進行役が次の変更に移るか、観察を続けるかを判断し、提案役が試す設定を考え、記録役が過去の結果を整理します。安全上の制約、統計による判定の基準、許された操作はプログラムで管理します。

著者は、利用者を分けた五つの実験グループを使い、従来のエージェント方式ROAMとPILOTを前後の期間で比較しました。最良グループの商品詳細ページへの訪問数は、共通の基準に対してROAMで1.00%、PILOTで1.40%増加。目標を上回る、測定が安定する、探索が前進するという三条件について、五つのグループを通じた達成割合は53.3%から93.3%に上がりました。比較したのは別々の時期です。進行役と提案役がそれぞれどれだけ効果を上げたかは分かりません。

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

LLMの候補品質、逐次検定、多重比較補正、sample ratio mismatch検出、実trafficの承認workflow、PolicyTreeの5 action全実装、memoryのsupersessionと規定に基づく対立解消は未実装。人工guardが動くことからIPV改善や自律実験の安全性は導けない。

Performance / Scaling / Production applicability: NOT TESTED。モデル学習とオンラインA/Bは実行していない。

[一次PDF](https://arxiv.org/pdf/2608.18637v1)。版・ハッシュ・節とコードの対応はmapping.md。公式コードは確認範囲で案内を見つけられず、実行していない。

記憶の小実験は証拠を順番に読み、反証が来た時点の状態を保持して昇格を止める。その後の支持も含め、全観測を保存する。同一taskの複製は昇格に寄与せず、inconclusiveは中立。approvedの閾値3はLabの仮定で、論文の固定値ではない。Curator全体の再現ではない。

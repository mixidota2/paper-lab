# Once Generated, Ranked: End-to-End Generative Slate Recommendation with Unified Semantic-Collaborative IDs

OGRは表示するslate全体を順序付きで生成する。TUSIDで意味と共起をSIDへ統合し、GL2Pが位置間の好みを計画、SPAがslate単位の反応へ合わせる。Kuaishouの3%トラフィックで有効視聴+1.120%。ただし約2.2倍は依存経路の理論比であり、本番遅延の測定値ではない。

## 読み方

OGR：生成した時点で、表示順も決まっている。まず問題設定と手法を読み、図で操作の単位を追う。Evidenceでは比較の分母と観察範囲を確認し、小実験と原論文の性能を分けて評価する。

著者は、推薦に適したSID、listwise planner、slate preference alignmentを組み合わせ、候補生成とrankingを分けずに順序付きslateを作れると主張する。

【Labの解釈】設計上の要点は、位置間依存をSID tokenの直列鎖から潜在的な好みの計画へ移すことにある。意味・共起の表現改善、依存経路の短縮、報酬の整列は別の効能なので、各々の根拠で判断したい。

## 再実行

```bash
uv run papers/ogr-once-generated-ranked/run.py
uv run paper-lab build
```

lab.yaml、method.md、mapping.md、run.py、results.jsonが原本。site/は生成物であり直接編集しない。実験は標準ライブラリのみ。

## 検証範囲

**Mechanism: PARTIAL**。人工条件の計算と境界条件を確認した。results.jsonのCONFIRMEDは小さな計算命題にだけ適用する。原論文の学習済みモデルや産業環境を再現した意味ではない。

融合部・SASRec・Transformer・RQ-KMeansの学習、SPA更新、実ログの露出bias、無効SID処理、online A/B、GPU throughputは検証していない。sketchの衝突が1回のhashで必ず相殺するとも主張しない。

Performance / Scaling / Production applicability: NOT TESTED。モデル学習とオンラインA/Bは実行していない。

[一次PDF](https://arxiv.org/pdf/2608.17613v1)。版・ハッシュ・節とコードの対応はmapping.md。公式コードは確認範囲で案内を見つけられず、実行していない。

# UniRec：SIDで失った属性を、生成の途中に戻す

UniRecは属性→SIDの順に生成し、候補生成とrankingの統合を狙う。Shopeeの各bucket 20%のA/BでOverall PVCTR +5.37%、orders +4.76%、GMV +5.60%。属性条件付きの不確実性低下は理解しやすい一方、本文のBayesによるランキング同値性には追加条件が要る。

一次資料：[2604.12234v4.pdf](https://arxiv.org/pdf/2604.12234v4)。SHA-256と節・表の対応は[mapping.md](mapping.md)。詳しい方法は[method.md](method.md)、サイト本文の原本は[lab.yaml](lab.yaml)。

## 実行

```bash
uv run papers/unirec-chain-of-attribute/run.py
```

属性を完全観測できる4-token分布のentropyを計算し、露出capacityの貪欲repairを試す。大きすぎる単一商品の実行不能例も残す。さらにBayesの分母を省くと順位が反転する2商品の確率表を、補正あり/なしで比較する。

## 検証範囲

Mechanism PARTIAL。個別のCONFIRMED / NOT OBSERVEDは[results.json](results.json)のchecksに記録。Performance / Scaling / Production applicability NOT TESTED。

属性予測の誤り、full training、beam recall、RFT/DPOの学習、Shopee A/B、段ごとの削除効果はNOT TESTED。entropyの減少だけからCTR上昇や生成・判別の同値性を結論しない。

## 実装の位置付け

確認した論文本文・arXiv書誌には取得可能な公式実装の案内を確認できなかった。非公開であると断定せず、公式コードの独立実行はNOT TESTEDとする。

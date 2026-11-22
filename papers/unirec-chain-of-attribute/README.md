# UniRec：SIDで失った属性を、生成の途中に戻す

UniRecはカテゴリなどの商品属性を予測してからSIDを生成する。属性を手がかりに商品を絞り、候補生成と順位付けを一つのモデルで扱うことを目指す。Shopeeが各bucketに20%を割り当てたA/Bでは、Overall PVCTR +5.37%、orders +4.76%、GMV +5.60%を報告した。属性を手がかりにした場合としない場合で、次のSIDを予測する不確実性を比べる説明は追いやすい。属性を条件に加えても不確実性は平均では増えないが、生成と判別で商品の順位が同じになるかどうかは別の話だ。本文のBayesの式から同じ順位になると説明するには、分母を省ける条件を確かめる必要がある。

一次資料：[2604.12234v4.pdf](https://arxiv.org/pdf/2604.12234v4)。PDFのSHA-256と対応する節・表は[mapping.md](mapping.md)、モデルと式は[method.md](method.md)に記す。サイト本文の原本は[lab.yaml](lab.yaml)。

## 実行

```bash
uv run papers/unirec-chain-of-attribute/run.py
```

Labは属性が正しく分かる4-token分布で、属性ありと属性なしのentropyを比べる。露出の上限を超えたcluster（商品のグループ）から商品を移す貪欲法も試す。商品1個の露出が大きすぎて上限を守れない例を含めた。Bayesの式では2商品の確率表を使い、分母の補正を省いた順位と補正した順位が逆になることを確かめる。

## 検証範囲

MechanismはPARTIAL。個別のCONFIRMED / NOT OBSERVEDは[results.json](results.json)のchecksに記録した。Performance / Scaling / Production applicabilityはNOT TESTED。

属性予測の誤り、モデル全体の学習、beam recall、RFT/DPOの学習、ShopeeでのA/B、各段を外した場合の効果はNOT TESTED。entropyが下がるだけでは、CTRが上がるかどうかや、生成と判別で同じ順位になるかどうかは分からない。

## 実装の位置付け

確認した論文本文とarXiv書誌には、取得できる公式実装への案内が見当たらなかった。非公開とは断定せず、公式コードの独立実行はNOT TESTEDとする。

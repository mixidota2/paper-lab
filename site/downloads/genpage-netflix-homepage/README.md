# GenPage：候補集合の内側で、Netflixのホームを一つの列として作る

GenPageは行と作品の並びをdecoder-only Transformerで生成する。オンラインで試した約200MのWBCモデルは、既存の行・作品候補集合を使う。14日A/Bの最良variantで主指標+0.24%、end-to-end遅延−20%。候補生成まで全面置換した証拠とは分けて読む。

一次資料：[2606.31031v2.pdf](https://arxiv.org/pdf/2606.31031v2)。SHA-256と節・表の対応は[mapping.md](mapping.md)。詳しい方法は[method.md](method.md)、サイト本文の原本は[lab.yaml](lab.yaml)。

## 実行

```bash
uv run papers/genpage-netflix-homepage/run.py
```

2行×3作品の人工ホームに候補外の高score作品を置く。同じscore関数で無制約、全逐次、先頭1件のみ逐次、行全体一括を比較する。Aを選ぶとCのscoreが上がる設定により、行内条件付けが変わる場面を作る。forward回数は計算手順の数で、20%の遅延再現ではない。

## 検証範囲

Mechanism PARTIAL。個別のCONFIRMED / NOT OBSERVEDは[results.json](results.json)のchecksに記録。Performance / Scaling / Production applicability NOT TESTED。

Netflixデータ、reward system、200Mモデルの学習、ページ満足度、RLのオンライン効果、Gryphonとの実験比較はNOT TESTED。人工例でhybridと全逐次が一致しても、任意の相互作用で一致する保証はない。

## 実装の位置付け

確認した論文本文・arXiv書誌には取得可能な公式実装の案内を確認できなかった。非公開であると断定せず、公式コードの独立実行はNOT TESTEDとする。

# GenPage：候補集合の内側で、Netflixのホームを一つの列として作る

Netflixの研究チームは、ホーム画面に並べる行と、それぞれの行に載せる作品を、一つのTransformerで順に決めるGenPageを提案しました。利用者の視聴履歴やすでに表示した行を入力し、既存の候補集合の中から次の行と作品を選びます。

14日間のA/Bテストでは、約2億パラメータのモデルを従来の多段階の推薦と比べました。最も成績のよかった設定では、採用判断に用いる主要な利用指標が0.24%増えました（95%信頼区間は0.17〜0.30%増）。著者は、配信全体にかかる時間が20%短くなったとも報告しています。本番で試したのは、重み付きの二値分類で追加学習したモデルです。強化学習版や、既存の候補生成まで置き換える構成は、この本番比較の対象ではありません。

一次資料：[2606.31031v2.pdf](https://arxiv.org/pdf/2606.31031v2)。SHA-256と節・表の対応は[mapping.md](mapping.md)。詳しい方法は[method.md](method.md)、サイト本文の原本は[lab.yaml](lab.yaml)。

## 実行

```bash
uv run papers/genpage-netflix-homepage/run.py
```

2行×3作品の人工ホームに候補外の高score作品を置く。同じscore関数で無制約、全逐次、先頭1件のみ逐次、行全体一括を比較する。Aを選ぶとCのscoreが上がる設定により、行内条件付けが変わる場面を作る。一括で選ぶ部分では、その部分の途中で作品を追加してもスコアを計算し直さない。forward回数は計算手順の数で、20%の遅延再現ではない。

## 検証範囲

Mechanism PARTIAL。個別のCONFIRMED / NOT OBSERVEDは[results.json](results.json)のchecksに記録。Performance / Scaling / Production applicability NOT TESTED。

Netflixデータ、reward system、200Mモデルの学習、ページ満足度、RLのオンライン効果、Gryphonとの実験比較はNOT TESTED。人工例でhybridと全逐次が一致しても、任意の相互作用で一致する保証はない。

## 実装の位置付け

確認した論文本文・arXiv書誌には取得可能な公式実装の案内を確認できなかった。非公開であると断定せず、公式コードの独立実行はNOT TESTEDとする。

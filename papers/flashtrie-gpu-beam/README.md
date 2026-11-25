# FlashTrie：beam幅を広げる余裕を、GPUのtrie探索で作る

広告検索では、辞書にあるキーワードだけを候補に残しながら、検索結果を短時間で返す必要があります。FlashTrieは、途中まで作った候補を伸ばし、辞書に照らして確認し、有力な候補だけ残す処理をGPUにまとめます。

8億件のキーワード辞書を使い、各段階で残す候補の上限を1,000にした測定では、1リクエストの辞書探索は従来のCPU方式で平均46.3 ms、FlashTrieで平均1.9 msでした。FlashTrieの遅い側の目安である99パーセンタイルは3.3 msです。英語の広告検索を対象とした別の本番A/Bでは収益が0.71%増えましたが、この試験では処理先だけでなく探索で残す候補数も変えています。

一次資料：[2607.10044v1.pdf](https://arxiv.org/pdf/2607.10044v1)。SHA-256と節・表の対応は[mapping.md](mapping.md)。詳しい方法は[method.md](method.md)、サイト本文の原本は[lab.yaml](lab.yaml)。

## 実行

```bash
uv run papers/flashtrie-gpu-beam/run.py
```

前のtokenによって確率表を変えない非自己回帰（NAR）の設定を置き、2段の固定確率表からprefix制約付きbeam searchをCPUで実行する。beam1で落ちる最適系列がbeam2で残る例と、depth-only filterが無効な組合せを返す例を比べる。GPUの時間を測った実験ではない。

## 検証範囲

Mechanism PARTIAL。個別のCONFIRMED / NOT OBSERVEDは[results.json](results.json)のchecksに記録。Performance / Scaling / Production applicability NOT TESTED。

CUDA、Narrow-LOUDSのメモリ圧縮、800M index、teacher精度、30msのproduction SLO、収益はNOT TESTED。下のSLO操作は著者表の読み替えであり、新しい測定ではない。

## 実装の位置付け

原論文には、公式コードを査読後に公開する予定だと記されている。確認した一次資料から取得可能な公式実装は見つからなかった。MARISAは比較対象でありFlashTrie公式実装ではない。

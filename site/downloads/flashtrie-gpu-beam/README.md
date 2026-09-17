# FlashTrie：beam幅を広げる余裕を、GPUのtrie探索で作る

FlashTrieは圧縮trieとbeam展開・検査・選別をGPU内へまとめる。800M keyword列の測定では平均0.6–1.9ms、p99は最大3.3ms。オンラインEnglish revenue +0.71%、遅延−32%は、backendと実行可能なbeam構成を同時に変えた比較である。

一次資料：[2607.10044v1.pdf](https://arxiv.org/pdf/2607.10044v1)。SHA-256と節・表の対応は[mapping.md](mapping.md)。詳しい方法は[method.md](method.md)、サイト本文の原本は[lab.yaml](lab.yaml)。

## 実行

```bash
uv run papers/flashtrie-gpu-beam/run.py
```

2段の固定NAR確率表からprefix制約付きbeam searchをCPUで実行する。beam1で落ちる最適系列がbeam2で残る例と、depth-only filterが無効な組合せを返す例を比べる。GPUの時間を測った実験ではない。

## 検証範囲

Mechanism PARTIAL。個別のCONFIRMED / NOT OBSERVEDは[results.json](results.json)のchecksに記録。Performance / Scaling / Production applicability NOT TESTED。

CUDA、Narrow-LOUDSのメモリ圧縮、800M index、teacher精度、30msのproduction SLO、収益はNOT TESTED。下のSLO操作は著者表の読み替えであり、新しい測定ではない。

## 実装の位置付け

本文は査読後公開予定とする。確認した一次資料から取得可能な公式実装は見つからなかった。MARISAは比較対象でありFlashTrie公式実装ではない。

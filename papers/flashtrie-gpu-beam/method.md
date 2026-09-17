### 圧縮表現とGPU実行は別の工夫

§2.1–2.2。MARISA由来のLOUDS構造を整数tokenへ拡張する。labelとsuffix indexを2-byteのlow部と、必要なnodeだけのbit-packed high部へ分け、32-bit tokenを扱いつつ支配的な配列を縮める。800M keyword列のindexは約3.1GBでA100 80GBのHBMに収める（§4.1）。

一つのpersistent cooperative kernelが全T stepを処理する。active beamをCTAへ割り当て、512 threadsでtop-K展開とchild lookupを分担。子のtokenはbinary searchで検査し、候補をlock-freeに追加して、grid同期後にparallel merge sortでtop-Bへ落とす（Algorithm 1、Appendix D）。

scoreは `σ′ = σ + log p(x_t | x_<t)`。存在しないprefixは展開しない。これは各深さで出現可能なtokenだけを許すPPT filterより強い条件だ。深さごとに有効でも、組み合わせた列が存在するとは限らない。

### 実験はNARの提案表も使う

§3、Appendix E。産業workloadは語彙2.2M、800M keyword列、13,000 requests。production NARモデルの位置別top-K proposal gridを使い、BW=Kを100–1000で動かす。モデルの提案生成とtrie-search時間を混同しない。単一A100 80GBとAMD EPYC 7V13を使い、CPU MARISA-Optは8 workersで比較する。

公開workloadではNQ+GENREの3,600 queries、約6M title trie、T=16を使う（§4.7）。本番の全stackにこのCPU/GPU構成をそのまま当てはめたわけではない。Appendix Gのproduction controlはbeam200、top-k300、3-thread poolであり、30msのretrieval end-to-end SLAが基準になる。

出典：[2607.10044v1](https://arxiv.org/pdf/2607.10044v1)。上記で「Lab」とした式・条件は説明用の補助である。


<figure class="teaching batch17"><h3>GPUに残す四つの処理</h3><div class="b17-cards"><div><strong>展開</strong><p>beamごとにCTAを割り当て、top-Kの提案を並列に読む。</p></div><div><strong>検査</strong><p>圧縮trieの子をbinary searchし、有効prefixだけ残す。</p></div><div><strong>選別</strong><p>heapの逐次更新を避け、候補をmergeしてtop-Bへ。</p></div><div><strong>同期</strong><p>grid barrierを通り、次のdepthもdevice内で続ける。</p></div></div><figcaption>§2・Algorithm 1・図4。GPU kernelの模式分解。時間比率を推測して付けていない。</figcaption></figure>

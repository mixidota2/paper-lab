# Proximal Residual Value Functions for Consistent Planning and Real-Time Execution

**Worth。** 届いた在庫を一度に配る場合と、到着のたびに配る場合で、最後に各拠点に残る在庫は同じになるか。Amazon SCOTの著者らは、一致する条件を示し、配置後の在庫を同じ式で評価するState-proxを提案した。

未知の商品と別の期間を使ったオフライン評価では、過去の運用を模した比較方策の費用を1とすると、State-proxのSCPUTは0.950だった。需要を満たした数量当たりの配送・移送費用が5.0%低かったことを示す。現場のA/Bテストではない。

## 読む順番

`lab.yaml` の問題設定と根拠から始め、[手法の説明](method.md)で式と配置図を対応させる。[原論文との対応](mapping.md)には、実装した範囲を記した。著者報告とLabの検算値は `results.json` で分けている。

## 実験を動かす

```sh
UV_CACHE_DIR=/tmp/uv-cache uv run --no-project papers/proximal-residual-value-inventory-placement/run.py
UV_CACHE_DIR=/tmp/uv-cache uv run paper-lab build
```

図3・付録C.1の2拠点例を解く。H=[[2,3],[3,5]]、a=(0,1)、線形費用0で、総入荷量2を1・2・5・20・500回に分ける。一度置いた在庫は戻せない。

同じ初期在庫と総入荷量で、二つの比較例を試せる。一つは区分線形（PWL）の残差に、配置後の在庫にかかる二次の項を加える。もう一つは二次の項をその回に置く量にかける。総入荷量が同じなら一方の拠点への配置量から他方も決まるため、配置は一変数の凸最小化として二分探索で解ける。論文のState-proxソルバー、エントロピー型の項、逆伝播は実装しない。

## 確認できたことと未検証の範囲

- **CONFIRMED（図3の反例）**：Hが正定値でも一括と分割の配置が一致しない。H⁻¹1=(2,−1) の負成分は、入荷総量が増えるのに最適な在庫が減る拠点があることに対応する。
- **PARTIAL（状態ポテンシャル）**：拠点ごとに分けられるPWL残差と二次の項だけを数値で確かめた。各回の配置量に項を加える比較例はLab独自で、表1の再現ではない。
- **NOT TESTED**：強化学習、State-proxの陰関数微分、Gurobiへの再構成、0.950という費用改善、100万商品の規模、現場導入。入荷の間に需要や費用が変わると生じる配置差は、論文でも解決していない。PCSPの定理は、連続量を一つの総量配分制約の下で割り振り、環境が一定の場合に限る。

一次資料：[論文](https://arxiv.org/abs/2609.23242)。公開ページ：[Lab](https://mixidota2.github.io/paper-lab/papers/proximal-residual-value-inventory-placement.html)。

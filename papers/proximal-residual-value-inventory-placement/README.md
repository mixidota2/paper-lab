# Proximal Residual Value Functions for Consistent Planning and Real-Time Execution

Worth — 在庫の配置先を学ぶState-prox。分割配置の整合性をPCSPで特徴付け、オフライン費用を5.0%削減。

入荷在庫をどの拠点へ置くかを学ぶ研究。Amazon SCOTの著者らは、区分線形の残差関数と強凸な状態potentialを組み合わせ、計画と実行で同じ凸目的を使うState-proxを提案した。歴史的運用の代理方策に対するオフラインSCPUTは、未知商品・別期間で0.950、5.0%改善。現場A/Bは行っていない。

## 読む順番

lab.yamlの問題設定と根拠を読み、[手法の説明](method.md)で式と図を対応させる。[原論文との対応](mapping.md)には最小実装の省略点を記した。著者報告とLabの検算値はresults.jsonで分離している。

## 実験を動かす

```sh
UV_CACHE_DIR=/tmp/uv-cache uv run --no-project papers/proximal-residual-value-inventory-placement/run.py
UV_CACHE_DIR=/tmp/uv-cache uv run paper-lab build
```

図3・付録C.1の2拠点反例をそのまま解く。H=[[2,3],[3,5]]、a=(0,1)、線形費用0で、入荷合計2を1・2・5・20・500回に分ける。各配置は後から引き戻せない。

同じ初期状態と入荷量で、Labが用意した分離可能PWL残差＋二次状態potential、PWL残差＋行動正則化も比べる。一次元の凸最小化へ落とし、二分探索で解く。論文のState-proxソルバー、エントロピーpotential、逆伝播は実装しない。

## 確認範囲を守る

**CONFIRMED — 図3の反例**：正定値Hの下でも配置が一致しないこと、H⁻¹1=(2,−1)の負成分と減少する経路の対応を確認した。

**PARTIAL — 状態potential**：分離可能なPWL残差と二次potentialだけを数値確認した。独自の行動正則化との比較は論文表1の再現ではない。

**NOT TESTED**：RL学習、State-proxの陰関数微分、Gurobiへの再構成、0.950という費用改善、100万商品への規模、現場導入。入荷間の需要や費用変化によるenvironment-perturbation errorは、論文自身も解決していない。PCSPの定理は連続・単一simplex・固定環境の条件を外せない。

一次資料：[論文](https://arxiv.org/abs/2609.23242)。Pages：[Lab](https://mixidota2.github.io/paper-lab/papers/proximal-residual-value-inventory-placement.html)。

# Risk-Aware Decision-Focused Demand Forecasting for Multi-Channel Inventory Optimization under Promotion and Stock-Out Constraints

Radar — M5でRA-DFLはPTO比−3.7%。CVaRの後付けは+9.7%悪化。代理指標と引用上の懸念からRadarを維持。

RA-DFLは、需要分布の予測を平均費用と裾の費用で学ぶ。M5ではLightGBM-QRのPTO費用4.903に対して4.721、3.7%改善した。一方、同じPTO予測にCVaR判断だけを後付けすると5.380、9.7%悪化した。どちらも著者報告で、本Labの再学習結果ではない。

判定はRadarを維持する。掲載先はHighlights in Business, Economics and Management、MSIED 2026、Vol.69。販促と欠品は代理指標で、評価需要は観測売上だ。本文中の引用の関連性や結果の記述にも確認すべき点が残る。

## 読む順番

lab.yamlの問題設定と根拠を読み、[手法の説明](method.md)で式と図を対応させる。[原論文との対応](mapping.md)には最小実装の省略点を記した。著者報告とLabの検算値はresults.jsonで分離している。

## 実験を動かす

```sh
UV_CACHE_DIR=/tmp/uv-cache uv run --no-project papers/ra-dfl-risk-aware-decision-focused-inventory/run.py
UV_CACHE_DIR=/tmp/uv-cache uv run paper-lab build
```

容量10の2チャネルで、66通りの整数配分を全探索する。10個の固定需要シナリオ、保有費用1、欠品費用6、横持ち費用1、横持ち可能率0.4を全条件で共有する。リスク重みwを0〜1に変え、平均費用とCVaR₀.₈の配分を比べる。

別実験では横持ちを0にし、観測売上4・真の需要10について通常損失とmasked lossを比較する。需要・売上・発注量の格子でも下界を検算する。予測器の学習、fill-rate罰則、連続配分の微分可能ソルバーは含めない。

## 確認範囲を守る

**CONFIRMED — 限定計算**：有限シナリオのCVaR、容量制約下の整数全探索、横持ちなしのmasked loss下界を検算した。

**PARTIAL — メカニズム**：平均と裾の配分、および余剰罰則の除去を分けて確認。一般の横持ちを含む命題2や、その損失の最小化が不偏になるという主張までは確認していない。

**NOT TESTED**：M5・Stallionの再学習、微分可能層の最適性gap 0.32%、LightGBM-QRとの3.7%差、CVaR後付けの9.7%悪化、実店舗の欠品・費用。ChronosなどTSFMとGBDTの条件をそろえた比較でもない。

価格低下を販促、週内のゼロ売上列を欠品とするproxyであり、真の在庫可用性や潜在需要を観測していない。LightGBMを含む比較経路で意思決定指標の空白を一部埋める研究として追い、Radarから引き上げるには再現と測定条件の確認が必要だ。

一次資料：[論文](https://hbemdata.org/index.php/ojs/article/view/198)。Pages：[Lab](https://mixidota2.github.io/paper-lab/papers/ra-dfl-risk-aware-decision-focused-inventory.html)。

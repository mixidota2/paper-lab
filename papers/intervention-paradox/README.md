# 介入の逆説：失敗を当てても、止めるほど成功が減ることがある

Accurate Failure Prediction in Agents Does Not Imply Effective Failure Prevention

Writerの著者はエージェントの失敗を予測できれば、実行途中に巻き戻したり助言を加えたりして成功率を上げられるかを調べました。失敗を見分けるモデルのAUROCは約0.94でした。著者は同じ課題を介入ありとなしで比べ、介入で失敗から成功に変わった件数と、逆に成功を崩した件数を数えました。

質問応答のHotPotQAではMiniMax-M2.1の実行を途中で巻き戻すと、成功率は64%から38%に下がりました。一方、ALFWorldでQwen-3-8Bに助言を加えた設定では、成功率は5.8%から8.6%に上がりました。どちらもベンチマークでの結果です。失敗予測の精度だけでは、介入で成功が増えるかは判断できません。

一次資料：[arXiv 2602.03338v1](https://arxiv.org/pdf/2602.03338v1)。判定：Worth Reading。

## 読み方

lab.yamlが本文と図の定義、method.mdがモデル・数式の補足、mapping.mdが一次資料との対応表。run.pyが最小実験、results.jsonが実行結果。siteは生成物である。

## 実行

```sh
uv run papers/intervention-paradox/run.py
uv run paper-lab build
```

## 検証の境界

対応した最終結果の数え方と閾値を計算し、全成功・全失敗・変化ゼロの境界を分けた。合成pilotで、正の期待効果があっても50タスクでは導入判断を誤り得ることを確かめた。

criticの学習、AUROC、LoRA、温度較正、ROLLBACKの環境復元、APPENDの実際のLLM反応、論文p値は未再現。50タスクで安全を保証する手法ではない。domain移行時にr/dを持ち越せるか、AgentTether等の複雑な修復でも同じ率になるかは未検証。

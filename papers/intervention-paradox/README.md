# 介入の逆説：失敗を当てても、止めるほど成功が減ることがある

Accurate Failure Prediction in Agents Does Not Imply Effective Failure Prevention

Writerの研究は、失敗予測のAUROCが約0.94でも実行途中の介入が有害になり得ると示す。必要なのは救えた失敗と壊した成功の対応比較だ。MiniMax-M2.1のHotPotQAでは64%→38%（−26ポイント）、Qwen-3-8BのALFWorldでは5.8%→8.6%（+2.8ポイント）。いずれもベンチマーク実験で、稼働中の製品全体の成功率ではない。

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

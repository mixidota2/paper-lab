# AgentX：発案数と採用率を分けて、推薦開発の自動化を読む

AgentXは発案、実装、オンライン評価、harness更新を閉じた開発ループにする。3 workers・3週間で374案から10件のlaunchable results。8倍の同時実験と3.7倍のworker-weekあたり価値は運用観察であり、同じ案を人とagentへ割り付けた比較ではない。

一次資料：[2606.26859v2.pdf](https://arxiv.org/pdf/2606.26859v2)。SHA-256と節・表の対応は[mapping.md](mapping.md)。詳しい方法は[method.md](method.md)、サイト本文の原本は[lab.yaml](lab.yaml)。

## 実行

```bash
uv run papers/agentx-kuaishou/run.py
```

同じ主効果とCIに対し、guardrailがclear、moderate、severeの場合、観測が短い場合、有意でない場合を比較する。別に同一3-taskの新旧score差でSGPOの採否を計算する。効果閾値0.2、最小14日は説明用の仮定で、AgentXの固定規定ではない。

## 検証範囲

Mechanism PARTIAL。個別のCONFIRMED / NOT OBSERVEDは[results.json](results.json)のchecksに記録。Performance / Scaling / Production applicability NOT TESTED。

LLMによる発案・coding、統計推定器、production rollout、SGPOの改善率、workerのスケーリング、人間との同条件比較はNOT TESTED。guardrail recordの計算は機構の一部だけである。

## 実装の位置付け

確認した論文本文・arXiv書誌には取得可能な公式実装の案内を確認できなかった。非公開であると断定せず、公式コードの独立実行はNOT TESTEDとする。

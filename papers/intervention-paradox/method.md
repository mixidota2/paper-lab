### 2×2の結果表から、母数の異なる率を作る

Aは両方失敗、Bは介入なしで成功・ありで失敗、Cは介入なしで失敗・ありで成功、Dは両方成功。F=A+C、S=B+D、N=F+Sと置く。回復率r=C/Fと破壊率d=B/Sは分母が違う。回復件数Cと破壊件数Bの比とは一致しない。

成功率差は(C+D)/N−(B+D)/N=(C−B)/N。これにC=Fr、B=Sdを代入するとp r−(1−p)dになる。r+d>0なら、改善の境界はp*=d/(r+d)。これはtask群のbaseline失敗率の境界であり、個々のactionに介入するcriticの閾値τ=0.6とは別の量だ。[式1–4](https://arxiv.org/pdf/2602.03338v1)

### ROLLBACKとAPPENDで、訂正の受け方が変わる

実験のagent backboneはQwen-3-8B、GLM-4.7、MiniMax-M2.1。ROLLBACKは直前actionを取り消し環境状態を復元して再試行、APPENDはactionを実行したまま警告を追加する。各taskのaction予算は15、介入予算は3。criticはQwen3-0.6B、温度Tをモデル別validationの負の対数尤度で合わせる。

Qwen3-14B criticの4設定も試すが、最良AUROC 0.927は0.6Bの0.936を超えない。これは同データ条件の識別性能比較で、大きいcriticは一般に役立たないという結論ではない。HotPotQAのτ sweepでも最良τ=0.7はbaseline 57%に対して54%。閾値だけで取り戻せなかった条件がある。[§3、§5](https://arxiv.org/pdf/2602.03338v1)

### 原論文内の不整合は、定義と表を優先して読む

§4の「回復件数が破壊件数より多い」をd/r<1と結ぶ記述は、分母の違う率では成立しない。正しい条件はp r>(1−p)dである。付録GのMiniMaxの7.3:1という比も、付録D表21のr≈0.12・d≈0.35（約2.9）とは整合しないため、このLabの計算には使わない。

ALFWorld本文にはfull評価のROLLBACKも+4.7ポイントという記載があるが、表4・17は非較正ROLLBACK 7.9−5.8=+2.1ポイントを示す。+4.7はpilotの記載と分離し、本評価の代表値には表のAPPEND +2.8を採る。また「ALFWorldで悪化なし」は表4のGLM Cal+App −1.3ポイント等と一致しない。oracleの本文の範囲も表10と違うため、表10のHotPotQAでは介入+4.0〜7.7、Best-of-2 +6.7〜11.0ポイントと限定して読む。oracleは実装済みの達成性能ではない。

### 修復技法の優劣より先に、導入前後の成功を対応させる

[AgentTether Lab](agenttether-repair.html)は診断に基づく修復、[REVISE Lab](revise-recovery.html)は実行中の指示変更に伴う妥当性と再利用を扱う。本論文は特定の修復技法を置き換えるのでなく、その技法を入れた結果のBとCを測る判断枠として読める。直接の比較実験はない。

[MAP（Measuring Agents in Production）](https://arxiv.org/abs/2512.04123)は開発者の調査・事例を通じて本番の運用を調べる研究だ。MAPの運用実態と、この論文のベンチマーク成功率は母集団が違う。人間への引き継ぎを含む製品の安全性へ、ここでのr/dや−26ポイントを直接当てはめない。

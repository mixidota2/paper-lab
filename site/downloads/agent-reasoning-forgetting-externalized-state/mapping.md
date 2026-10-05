# 原論文との対応

一次資料：[When Can Agents Forget Their Reasoning? v1](https://arxiv.org/pdf/2609.29875v1)、2026-09-24、全30ページ。本文・付録を照合した。

| 原論文 | Labの対応 | 省いた内容 |
| --- | --- | --- |
| Fig. 2 / Eq. 1–9 / Appendix C | READMEの手順と式 | DeepSeek実行、Qwen採点、block剪定は未実装 |
| Eq. 15 / Table 14–15 | 保存先の比較、results.paper.risk | 状態群の観察比較を因果効果へ変換しない |
| Table 16–17 | replay()の読出しと再導出 | Office課題・実tool・stderrの9介入は未再現 |
| Fig. 3 / Table 10 | Random 5/10/20/40%の散布図 | block削除のICLRをtoken削除と同じ横軸に置かない |
| Table 2・7 | Full260の報酬・費用 | 非公開軌跡の再評価なし |
| Table 3・9 | Ablation80でICLR 0.7376、全削除0.7178 | 260課題の0.717775との混同を訂正 |
| Theorem B.3 / Corollary B.4 | 行動分布差の累積上界と外部化の十分条件 | εの推定、適応的削除の安全性保証なし |
| Table 12–13 | probe・patchingの評価範囲を解説 | 実行役に対するpatchingはない |

run.pyは独立に書いた教育用の状態機械。公式コードの移植ではない。PDF本文・再現性記述には公式コードURLを確認できず、lab.yamlのofficial_codeはnullとした。原論文の公開状況全体を調査した主張ではない。

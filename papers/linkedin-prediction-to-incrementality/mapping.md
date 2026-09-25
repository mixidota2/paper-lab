# 原論文と最小実装の対応

一次資料：[From Prediction to Incrementality](https://arxiv.org/abs/2608.10182)、提供されたv1 PDFと抽出本文。Fig. 1はPDF画像でも確認した。提供論文内に公式コードへのリンクは見当たらず、公式実装の実行はNOT TESTED。

| 原典 | Labの対応 | 省略と確認範囲 |
|---|---|---|
| Fig. 1、§2.1、§3 | method.md、三段の数式図 | Transformer、DragonNet、outcome embeddingの学習は省略 |
| Eq. 1 | run.pyのmu1−mu0、人工期待値表 | 既知の平均。因果推定精度は測らない |
| §2.2.1 | LLAのlogit分散の式 | 最終層曲率、posterior samplingは未実装 |
| Eq. 3、§5.4 | allocate()、予算選択UI | 4人1施策、全探索。負の増分保留を確認 |
| Eq. 4、§2.3.1 | method.mdの射影式 | 双対分解、平滑化、warm startは未実装 |
| §5.1 | 入力・処置・成果の時間窓 | 日付設計の読解のみ。ログ作成は未実施 |
| Eq. 12–14、§5.2 | 割付と実配信の説明 | 配信確率の校正と制御器は未実装 |
| §5.4–5.5 | Evidence、README | 50/50、8週間、LTV +7.20%、p=0.041、95% CI [0.31%, 14.09%]は著者報告 |
| §5.4 | agentic campaign scaffoldingの説明 | segment系譜監査やcampaign複製は実行しない |

比較マップは本Labの解釈である。Netflixの観測、Spotifyの二閾値、PinterestのCG gatingと、LinkedInの制約付き配分を読み分ける。四論文の数値を同じ尺度で比較したり、各社の仕組みが相互に優越すると主張したりするものではない。

保存PDFのSHA-256：`9dec368311033e10b8b4ab1a8d298917fb3284edcc93ae12d3519c9196489be8`。

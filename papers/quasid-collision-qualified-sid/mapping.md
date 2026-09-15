| 原論文の場所 | Labの対応 | 範囲 |
| --- | --- | --- |
| 式1–7、Figure 2 | tokenizer＋協調学習の説明 | full modelの学習は未実装 |
| 式8、§4.2.1 | `qualified()` | 正例の位置と同一itemの除外 |
| 式9–13 | `pair_loss()` / `hamr()` | Hamming、cosine、群別平均を計算 |
| 式14 | 4損失の結合図 | 再構成・RQ・contrastiveはtoyに含めない |
| Table 4 | online cardsとcold-start表 | 著者報告。介入ごとに分離 |
| Appendix A.2 | 半径とmargin | 産業R=2、mfull=.8、mpartial=.5をtoyへ使用 |

[全文v1](https://arxiv.org/html/2603.00632v1)を本文からAppendix A.2まで通読。QuaSID自身の公式コードは本文・書誌で未確認。Appendix A.2が挙げる[基盤実装 RQ-VAE-Recommender](https://github.com/EdoardoBotta/RQ-VAE-Recommender)は別プロジェクトであり、QuaSIDの公式公開実装として登録していない。Labのコードは独自作成。

[CRID一次資料](https://arxiv.org/html/2607.11392#S2.SS1)の§2.1を確認し、cluster内の順位による一意性と日次更新を手法の位置付けに参照した。ISD・GR4AD・TAGRは既存Labの原典対応を参照し、結果を転用しない。原論文HTMLの仮置きDOI・会議テンプレート情報は正式書誌として採用しない。

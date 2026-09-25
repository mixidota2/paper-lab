# 原論文と実装の対応

一次資料は [原論文 v1](https://arxiv.org/abs/2609.28383)。提供された PDF とその抽出テキストを使った。PDF のハッシュは lab.yaml に記録する。ページの HTML は lab.yaml、README.md、method.md、run.py、results.json から生成する。

| 原典 | 本 Lab の対応 | 省略・境界 |
| --- | --- | --- |
| Fig. 1、§3.1 | 同じ平均・動画長の人工二群 | 実データの分布ではない |
| Fig. 2、Eq. 4 | run.py の state() | 四状態の比率境界を維持 |
| Eq. 5–6 | support と masked_mass | 0〜20秒の格子。69 bin の学習なし |
| Eq. 7、9–10 | summarize() | 平均・状態確率・long 確率・状態エントロピーのみ |
| Eq. 8 | lab.yaml の式と説明 | 復元損失の最適化は未実施 |
| Eq. 11–14 | 読み出しの数式説明 | DCNv2 学習は未実施 |
| Table 1、Fig. 3、Table 2 | Evidence | 著者報告。独立再現ではない |
| Appendix E、Table 9–10 | Why It Might Work | 通常の分布要約でも同程度という対照を併記 |
| §4.4、Table 3–4 | 転用結果の範囲を説明 | 転用実験は未実施 |

論文1ページ目は [公式コード](https://github.com/Xuanxuana1/DSI) を案内する。今回、公式リポジトリのファイル対応の監査や実行は行っていない。最小実装を公式コードの抜粋として扱わない。

本番 A/B の結果は原論文に報告されていない。事業効果は未確認。

保存PDFのSHA-256：`fe20b8854c01f2fe258be729b71d9d2ea25c71e03893e56a833b8f16593ec86d`。

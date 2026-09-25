# Original Paper / Official Code Mapping

一次資料は [ANGLE v1](https://arxiv.org/pdf/2609.18296v1)。対象はv1のみ。提供されたPDFと抽出テキストを使用した。著者によるコード公開先は本文に見当たらず、公開の有無は未確認。

| 論文の要素 | 一次資料の位置 | Labの対応 | 境界 |
|---|---|---|---|
| intent × abstractから広告集合へ | §3.3、表1、図3 | `run.py:index_ads`、索引の行列表現 | 語句は手作業。Hunyuan-13Bは実行しない |
| DCBSの有効候補への制約 | §3.4、図3 | `run.py:retrieve`の事前filter | token単位の木を組単位のtop-kへ縮約 |
| 新広告の索引更新 | §3.3、§4.1 | `run.py:main`のF追加 | 正しい組は手で与える。意味的汎化の検証ではない |
| 生成・関連性・DPO | §3.2、図1、式4〜6 | `lab.yaml`の数式図、`method.md` | 損失は説明のみ。学習しない |
| オフライン性能・分解実験 | 表2・4 | Evidence | 著者報告。実データでの再実行なし |
| WTSのオンライン指標 | 表3、§4.2 | 棒グラフとEvidence | 表3の+1.81%を採用。本文の+1.18%との不一致を明記 |
| rankingを残す制約 | §4.2、Limitations | Overview、Evidence | 自然検索や推薦全体への一般化をしない |

## 省いた実装

広告とクエリのSFT、Hunyuanの推論、discriminator、DPO、token単位のbeam探索、オンライン配信条件の取得、ANN baseline、分散した索引更新を省いた。比較するのは取得集合だ。売上は算出しない。商用価値も未評価。

## 生成物の出所

`lab.yaml`は日本語本文と図の定義、`README.md`は読解用の本文、`method.md`は手法の補足を保持する。操作画面は`run.py`の計算結果に対応する6条件を埋め込む。`results.json`は実行結果で、HTMLはサイトの共通generatorが生成する。

保存PDFのSHA-256：`f5c84a5a3b3ef9683b441f265e358c1f1fa446e4656265bb8dbaeb93ce29a7ef`。

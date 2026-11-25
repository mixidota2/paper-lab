# 論文初版、公式の動作例、このLabの対応

[論文初版（arXiv v1）](https://arxiv.org/html/2608.18779v1)は、本文、実験、限界、付録を2026-09-21に確認しました。保存したHTMLのSHA-256は `8043cc1a9924d9a3fd53d1d786c74d17dc91844fbd59550df933fb87c5c16fa8` です。

| 論文の箇所 | Labで行うこと | Labで扱わないこと |
| --- | --- | --- |
| §3.2：D1、D2、D5 | `diagnose()` で符号の利用や重複を調べる | ジニ係数、人気別のD4 |
| §3.2：D3 | 渡された商品対で、先頭の符号の一致を重み付きで調べる | 公式手順で利用履歴から商品対を選ぶこと |
| §6.3：D6 | 更新前の表を渡し、符号が変わった割合を計算する | 学習済みモデルの適応 |
| §5：D7 | `trace()` で符号の有効性、曖昧さ、正解を一つに特定できるかを調べる | 公式ログのすべての分類 |

## 以前に公式の動作例で確認した範囲

[公式コードのv1.0.1](https://github.com/jdding/sidscope/tree/v1.0.1)で `examples/run_reviewer_quickstart.py` を実行し、入力検査の通過とD1〜D5の出力を確認しました。12商品の公開入力を使う動作例で、本番の対応表ではありません。今回の改稿時に公式パッケージを実行し直してはいません。

異なる完全SIDの数11、D2の2/12、D5の重複率1/12、先頭から各段までの符号列の数3/6/11は、Labの独立実装と一致しました。一方、公式のD1は段ごとに単独の符号の偏りを計算し、Labはそこまでの符号列の偏りを計算します。2段目以降の情報量は同じ指標として比べません。

| 公式v1.0.1 | Labで対応する計算 |
| --- | --- |
| `src/sidinspector/metrics.py::collision` | `diagnose()` が返す `collision_item_rate` |
| `metrics.py::deployment_cost` | `unique_leaves`、`duplicate_SID_rate`、`active_prefixes` |
| `metrics.py::alignment` | 渡された商品対の重み付き集計だけ |
| `src/sidinspector/d7_trace.py` | `trace()` が行う有効・曖昧・一意の判定だけ |

以前取得した公式コードのアーカイブのSHA-256は `852f79c01075708fa0b9161bd686e31a7dc3a37ff7ef3d1b0625c5ed5b39a525`、入力CSVは `5ada9e4f9782dc12cb931fd54af86ac59fc78b65101d789d99b0fc984321dcaf` です。公式の実行記録は `official-check.json`、入力例のMITライセンスは `NOTICE.txt` にあります。

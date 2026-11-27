# 第2版の著者報告と、第1版に基づく計算の対応

記事の説明は[第2版](https://arxiv.org/html/2610.04433v2)を使います。Labの計算の入力は2026年10月8日に照合した[第1版のPDF](https://arxiv.org/pdf/2610.04433v1)に対応します。そのPDFのSHA-256は `c0c4899a732bb57aab9bac01fb64c83bc343c2a53e65554024ae292113726a32` です。

| 論文の箇所 | Labの対応 | 確かめた範囲 |
|---|---|---|
| 第2版 §4、表1〜3、付録M・Q | 記事の概要と結果 | 追加の再実行、組み合わせで逆転する成績、モデルによる費用差を著者報告として説明します。新しい試行の再集計はしていません。 |
| 第1版 付録F、図A2 | `binom()`、`rejection()`、`power()`、`mde()`、`simulation()` | 不一致件数が変動する場合の検出力を計算し、45課題と447課題の結果を乱数試行と照合します。 |
| 第1版 付録G、表A4 | `token_bill()` | 定型文と履歴が作る入力トークンを計算します。出力や実際の履歴圧縮、請求額は再現しません。 |
| 第1版 表1、§4.5 | `results.json` の `paper` | 第1版の条件と数値を記録しています。第2版の値を追加した試行表ではありません。 |

[著者の公開リポジトリ](https://github.com/YangzeLiu/what-does-a-harness-buy)のコミット `3f0c13208c8b71eefcf7b764e2372ac7200c3117` で、`analysis/paper_numbers.py` の `exact_power` と `mde_pp_exact`、および `reference_outputs/numbers.json` を読み、不一致率の入力を確認しました。スクリプト全体は実行していません。 `official-check.json` はこのときの値を記録したものです。

課題別の元データは `data/trials.csv`、有効な試行の選び方は `analysis/main_table.py`、入力トークンの内訳は `analysis/tab_a4_budget.py` にあります。Labはこれらの課題別の集計をやり直していません。

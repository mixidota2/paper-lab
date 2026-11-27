# 原論文と Lab の対応

一次資料：[The Hidden Costs of Forgetting v1](https://arxiv.org/html/2610.35496v1)（2026年10月26日）。著者は Fernando Vallecillos-Ruiz、Islem Bouzenia、Michael Pradel、Leon Moonen。

| 原論文の箇所 | Lab で読めること | Lab では再現していないこと |
| --- | --- | --- |
| §II-C、図1、§III-C | `run.py` の `lcp()` と `ledger()` で、前回と先頭から一致する入力と、通常料金を払う入力を分ける。 | 実モデルの KV キャッシュは起動しない。記号列で計算だけを確かめる。 |
| §III-B | 手法の節で、何を消すか、何を単位にするか、いつ消すかを説明する。 | Lab は一つの決まった位置を書き換える。著者の無作為な全構成を再実行しない。 |
| 表I〜III、§VI | 根拠の節に著者の比較を載せ、`results.json` の `reported` に主要な費用の集計を記録した。 | Lab は生の実行ログから著者の値を計算し直していない。 |
| §III-D、§VII | 手法の節で、100課題から求める区間が何を含むか説明する。 | 介入を繰り返した場合のばらつきや実際の請求額は検証していない。 |

Lab は公開本文と表を照合した。著者が配布した Figshare の実行ログと分析コードは確認していない。[論文の書誌情報](https://arxiv.org/abs/2610.35496)から版を確認できる。

関連する[推論履歴をどこまで消せるか](agent-reasoning-forgetting-externalized-state.html)では、必要な情報を別の記録から読み出せるかを扱う。このページでは、入力の順序が変わったときに何トークンを通常料金で数えるかを扱う。

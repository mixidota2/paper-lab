# Original Paper / Official Code Mapping

確認日：2026-09-17。一次PDF：[2604.12234v4.pdf](https://arxiv.org/pdf/2604.12234v4)。arXivの初回公開日：2026/04/14、確認した版の日付：2026/04/30。

SHA-256：`338c6b948306f69053f4dd5b0fbff1c5f7440c2ec22d0ba4f1d9e4dbed19da78`

参照PDF：`2604.12234v4.pdf`。既存のHTMLで参照箇所を探し、上記のPDFに版を固定して、本文、関連する表、付録を照合した。Labの図は説明用に作成したもので、原論文の画像を写したものではない。

| 原論文の箇所 | 確認対象 | Labと省略範囲 |
| --- | --- | --- |
| §3.2、式1–2、Algorithm 1、図2 | clusterごとの露出上限と、露出が一部のprefixに集中する問題 | run.py: capacity_repair。clusterの中心を固定し、1層に絞った。 |
| §3.3、式3–6、表2 | Bayesの式、CoA、属性あり・なしのentropy | run.py: entropy / compute。Bayesの分母を省くと順位が逆になる例はLabが用意した。 |
| §3.4–3.6、式7–28 | CDC、cross-attention、RFT+DPO | method.md。モデルや学習処理は実装していない。 |
| §4.1–4.2、表1・3・5 | オフライン比較と、推薦を出す面ごとのA/B | Evidenceに記載。オンラインで各段を外した比較の詳細は分からない。 |

## 公式コード

確認した論文本文とarXiv書誌には、取得できる公式実装への案内が見当たらなかった。非公開とは断定せず、公式コードの独立実行はNOT TESTEDとする。

## 独立再現の境界

属性予測の誤り、モデル全体の学習、beam recall、RFT/DPOの学習、ShopeeでのA/B、各段を外した場合の効果はNOT TESTED。entropyが下がるだけでは、CTRが上がるかどうかや、生成と判別で同じ順位になるかどうかは分からない。

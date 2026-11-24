# 論文と公開コードのどこをLabで確認したか

一次資料は[原論文のarXiv v1 PDF](https://arxiv.org/pdf/2609.13840v1)。2026-09-22に確認したPDFのSHA-256は `7dc61d06092ef0a22a85ca5896d9432bdf345dc878b03bf81e367799a1d7f70d`。2026-11-25 JSTに、[著者が公開したv1 HTML](https://arxiv.org/html/2609.13840v1)の§III–IVも照合した。

| 原論文・公開成果物 | Labで扱った内容 | Labが実行していないこと |
| --- | --- | --- |
| 式3–4、§III-D | `replay()` が注文を順に処理し、全明細を満たせるかを調べる | 4品目、入荷待ち2期間の人工例。価格とプラットフォームの違いは扱わない |
| 式6–7 | `normalize()` で値を正規化し、保存した中心と尺度で元に戻す | Chronos-2本体とarcsinhによる追加の変換 |
| §IV-A、`industrial_orderbook_38.csv` | 著者が公開したCSVの順位を使って相関と散布図を求める | 非公開の注文から集計をやり直すこと、信頼区間の推定 |
| 表V、§IV-D | 論文の補正結果と、同じ変換を説明する人工例を分けて示す | 学習と38手法の再比較 |
| 公式 `MANIFEST.md` | 著者の人工データRUFと機密の実注文データを区別する | RUF v2を使った一連の実験 |

[公式リポジトリ](https://github.com/sfcheng-research/icdm-2026-reproduction)のREADMEとManifestは2026-09-22に確認した。正規化に対応するスクリプトは `src/scripts/10_experiments/run_raf_instancenorm.py` と `run_synthetic_instancenorm.py`。`validate_38_complete.py` は、38手法に結果の欠落がないか、失敗した実験で別の手法の結果を代わりに使っていないかを調べる。Labは公式の全実験を動かしていない。

[公式CSV](https://raw.githubusercontent.com/sfcheng-research/icdm-2026-reproduction/main/results_release/industrial_orderbook/industrial_orderbook_38.csv)は2026-09-22に取得した。SHA-256は `36cec2e7a4bdaa718ecbd05989ebbc661b1020d0044dfeb8ca4349a05f7b3ff9`。Labは同じファイルを `author-orderbook.csv` として保存し、そこにある順位から散布図を作る。

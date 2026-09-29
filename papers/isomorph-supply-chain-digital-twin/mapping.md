# 原論文・公式コード対応

一次資料は[arXiv v3](https://arxiv.org/pdf/2605.12768v3)。PDFのSHA256はlab.yamlに記録した。

| 論文 | Lab | 省略した範囲 |
|---|---|---|
| Figure 1 / Table 11 | 13拠点・16辺の図 | 地理座標、辺別容量 |
| 式(21–22) | run.py simulate() | 商品間の共有容量 |
| Proposition 4.1 | 毎期の保存則assert | 全ネットワークの保存則 |
| Tables 3 / 5 | lab.yamlの比較表 | CIは本文で定義。各セルでは省略 |
| §6.2 | シナリオ集合によるForward UQの説明 | 基盤モデルの推論と被覆率 |

[公式リポジトリ](https://github.com/tuhinsahai/ISOMORPH)は論文に記載された公開先。コードの取得・実行・ファイル単位の照合は行っていない。公式実装との一致を確認済みとは扱わない。

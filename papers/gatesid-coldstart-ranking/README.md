# GateSID：新商品ほど意味を借り、成熟商品では行動を残す

GateSIDはSIDをranking特徴として使い、商品の成熟度に応じて意味と行動のattentionを混ぜる。生成decodeの手法ではない。Alibaba Internationalの2週間・総traffic 20%のA/BでGMV +2.6%、新商品（20日未満）+5.6%、追加遅延5ms未満を報告する。

一次資料：[2603.22916v2.pdf](https://arxiv.org/pdf/2603.22916v2)。SHA-256と節・表の対応は[mapping.md](mapping.md)。詳しい方法は[method.md](method.md)、サイト本文の原本は[lab.yaml](lab.yaml)。

## 実行

```bash
uv run papers/gatesid-coldstart-ranking/run.py
```

固定した2種類のattention logitsと履歴embeddingを使い、wを0から1まで動かす。共有attentionを両履歴へ適用した結果と、同じwで重み付けしたInfoNCEを計算する。成熟度からwを学習した曲線は作らない。

## 検証範囲

Mechanism PARTIAL。個別のCONFIRMED / NOT OBSERVEDは[results.json](results.json)のchecksに記録。Performance / Scaling / Production applicability NOT TESTED。

RQ-VAE学習、maturity gate学習、CTR/CTCVRのranking学習、AUC、online GMV、5ms制約はNOT TESTED。固定gateでの凸結合を確認しただけで、本番のcold-start改善を検証したわけではない。

## 実装の位置付け

確認した論文本文・arXiv書誌には取得可能な公式実装の案内を確認できなかった。非公開であると断定せず、公式コードの独立実行はNOT TESTEDとする。

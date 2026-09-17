# CORAL：推薦の設定を、予算内で継続的に見直す

CORALは候補源の予算やsegment別のserving処理を、数日ごとに更新するMetaのharness。videoのR3でsessions +0.16%、watch time +0.15%、追加serving費用なし。別surfaceの44%は初回の削減額の増加率であり、総費用−44%ではない。

一次資料：[2609.02730v1.pdf](https://arxiv.org/pdf/2609.02730v1)。SHA-256と節・表の対応は[mapping.md](mapping.md)。詳しい方法は[method.md](method.md)、サイト本文の原本は[lab.yaml](lab.yaml)。

## 実行

```bash
uv run papers/coral-meta-config-harness/run.py
```

3つの手作り予算提案を、非負・合計10以下の集合へEuclidean projectionする。既に実行可能な提案は保存する。離散menuも全列挙で最も近い実行可能な構成を選ぶ。初回節約10・元費用100という人工値で「節約額44%増」の分母を示す。

## 検証範囲

Mechanism PARTIAL。個別のCONFIRMED / NOT OBSERVEDは[results.json](results.json)のchecksに記録。Performance / Scaling / Production applicability NOT TESTED。

LLM推論、attribution、人の監督の削減、時系列のpolicy改善、online A/B、実際のserving costはNOT TESTED。予算射影が成功しても、目的関数Jの改善は確認していない。

## 実装の位置付け

確認した論文本文・arXiv書誌には取得可能な公式実装の案内を確認できなかった。非公開であると断定せず、公式コードの独立実行はNOT TESTEDとする。

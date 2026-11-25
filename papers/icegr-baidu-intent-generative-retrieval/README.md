# ICEGR: An Intent-Coherent End-to-End Generative Retrieval Framework for E-commerce Search

Baiduの研究チームは、検索した人の目的に合う商品を生成モデルで探す方法を提案しました。たとえば口紅とネックレスは商品としては似ていませんが、「恋人への贈り物」という同じ検索で選ばれます。ICEGRは、同じ検索でクリックされた商品や、商品につながった過去の検索語も使って商品IDを作ります。表示が少ない商品には学習用の検索文を補い、検索に合う商品だけを比べ、クリックや注文などの実績を使って、どちらを優先するかを学びます。

Baiduは本番トラフィックの20%を使い、2週間のA/Bテストを行いました。既存の検索システムに5億パラメータのICEGRを追加し、その上位候補の一部を最終結果に直接入れました。著者の報告では、既存方式に比べてクリック率が3.52%、注文数が15.96%、取引総額が7.53%増えました。比較では商品IDの作り方、学習方法、表示の仕方をまとめて変えています。この数字だけでは、どの変更が効いたかは分かりません。

公開ページ: https://mixidota2.github.io/paper-lab/papers/icegr-baidu-intent-generative-retrieval.html

## 実行

```bash
uv run papers/icegr-baidu-intent-generative-retrieval/run.py
```

Python標準ライブラリだけを使う。`lab.yaml` と `method.md` が解説の原本、`run.py` が最小実験、`results.json` が出力、`mapping.md` が原典との対応。HTMLは `uv run paper-lab build` で生成する。

## 検証範囲

Mechanism PARTIAL。Eq. 3のanchor付き伝播、anchor=1で元表現を保持する端点、Eq. 9の係数範囲とmarginに対する単調減少はCONFIRMED。

Performance / Scaling / Production applicability NOT TESTED。8B embedding・0.5B retrieval・0.6B relevance modelの学習、合成queryの品質、RQ-KMeans、DPO収束、Baidu A/Bは未実行。本文はmodelサイズを示すが、base checkpointの名前までは確認できないため推測しない。

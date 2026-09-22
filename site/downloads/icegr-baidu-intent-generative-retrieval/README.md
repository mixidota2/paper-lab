# ICEGR: An Intent-Coherent End-to-End Generative Retrieval Framework for E-commerce Search

Baidu検索でintent-aware SID、合成query SFT、関連性を守る選好学習を統合。2週・20% A/BでCTR +3.52%、注文 +15.96%、GMV +7.53%。最終表示への直接挿入枠を持つ。

公開ページ: https://mixidota2.github.io/paper-lab/papers/icegr-baidu-intent-generative-retrieval.html

## 実行

```bash
uv run papers/icegr-baidu-intent-generative-retrieval/run.py
```

Python標準ライブラリだけを使う。`lab.yaml` と `method.md` が解説の原本、`run.py` が最小実験、`results.json` が出力、`mapping.md` が原典との対応。HTMLは `uv run paper-lab build` で生成する。

## 検証範囲

Mechanism PARTIAL。Eq. 3のanchor付き伝播、anchor=1で元表現を保持する端点、Eq. 9の係数範囲とmarginに対する単調減少はCONFIRMED。

Performance / Scaling / Production applicability NOT TESTED。8B embedding・0.5B retrieval・0.6B relevance modelの学習、合成queryの品質、RQ-KMeans、DPO収束、Baidu A/Bは未実行。本文はmodelサイズを示すが、base checkpointの名前までは確認できないため推測しない。

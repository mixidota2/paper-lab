# Original Paper / Official Code Mapping

一次資料: [SIDInspector: A Mapping-First Diagnostic Resource for Semantic-ID Tokenizers](https://arxiv.org/pdf/2606.10375v1)、arXiv v1。2026-09-22確認。PDF SHA-256: `4fc33c243ac3dae6dcd04666b3ab85a677fcdc089531c5e8edd77aff78300cb5`。取得済みPDFは `/tmp/research-2026-09-22/2606.10375v1.pdf` を再利用した。

| 原典 / 公式入口 | Lab | 省略 |
| --- | --- | --- |
| §2 / sidinspector.preflight | validate | 全schema・provenance検証 |
| §3 / sidinspector.metrics | probe | train userからのbounded top-k構築 |
| Table 2 | Evidence | 各tokenizerの生成 |
| §5 / examples/minimal_adapter.py | READMEの実行入口確認 | 公式package gateは未実行 |
| tools/verify_package.py | 次段階の公式検証先 | clean-check追試は未実施 |

PDF記載v0.6と、2026-09-22取得main READMEのv1.0は別版。公式READMEのSHA-256は取得記録として下記に記す。

公式公開先: [https://github.com/jdding/sidinspector](https://github.com/jdding/sidinspector)。READMEを確認したが、全実験の再実行はしていない。

公式main README SHA-256: `ab9e9927ddf8d74725746714634c727f5255ec4b5f897272f2ad8a88a7f5fed0`。

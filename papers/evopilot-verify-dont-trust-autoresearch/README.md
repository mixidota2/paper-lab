# Verify, Don’t Trust: Agentic Model Development for Video Discovery Retrieval at Scale

EvoPilotは、ある動画の後に見る動画を探す検索モデルの開発で、実験結果を公平に比べるための仕組みです。担当者が実験計画を承認し、実行後には計画どおりの出力が得られたかを確かめます。実行が最後まで終わっても、指標の測り方が両群でそろっていなければ、モデルの良し悪しは判断できません。

候補を再採点する部分を追加した初期実験では、当たり率が22ポイント下がったという結論が出ました。しかし、両群が同じ候補数を指定したにもかかわらず、実際に評価に使った候補数は異なっていました。最初に問題を見つけたのは人の確認で、自動検査を強化したのはその後です。評価条件をそろえた後の別のオフライン比較では、著者は当たり率が3.20ポイント上がったと報告しています。

公開ページ: https://mixidota2.github.io/paper-lab/papers/evopilot-verify-dont-trust-autoresearch.html

## 実行

```bash
uv run papers/evopilot-verify-dont-trust-autoresearch/run.py
```

Python標準ライブラリだけを使う。`lab.yaml` と `method.md` が解説の原本、`run.py` が最小実験、`results.json` が出力、`mapping.md` が原典との対応。HTMLは `uv run paper-lab build` で生成する。

## 検証範囲

Mechanism PARTIAL。実現Kの反証probeと、pairの許可外差分・no-op・欠落の拒否は人工artifactでCONFIRMED。canonical recordのhashも計算する。

Performance / Scaling / Production applicability NOT TESTED。本番MBR学習、数億動画index、37日agent運用、offline +3.20 pp、online +0.66%は再現していない。local hashは遠隔artifactの真正性を保証しない。

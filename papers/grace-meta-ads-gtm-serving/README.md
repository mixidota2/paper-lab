# GRACE: Generative Recommender Acceleration Engine for Real-Time Ads Retrieval

SIDのbeam内に要求別targetingを入れ、最終広告pass率を23.55→40.42%へ改善。固定beam decoderの197.7→17.8 msと、GTM込み全体P99 53.6 msは別測定。

公開ページ: https://mixidota2.github.io/paper-lab/papers/grace-meta-ads-gtm-serving.html

## 実行

```bash
uv run papers/grace-meta-ads-gtm-serving/run.py
```

Python標準ライブラリだけを使う。`lab.yaml` と `method.md` が解説の原本、`run.py` が最小実験、`results.json` が出力、`mapping.md` が原典との対応。HTMLは `uv run paper-lab build` で生成する。

## 検証範囲

Mechanism PARTIAL。人工4要求で、適格広告を持つprefixがOR検査を通ることはCONFIRMED。属性相関の偽陽性、Bloomの偽陽性、同一beamの枠再配分を実行した。

Performance / Scaling / Production applicability NOT TESTED。GH200 kernel、KV cache、production targeting全条件、実pass率、広告A/Bは未実行。CPUの4広告を23.55→40.42%の再現とは呼ばない。

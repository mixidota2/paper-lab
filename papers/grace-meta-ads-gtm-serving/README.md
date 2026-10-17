# GRACE: Generative Recommender Acceleration Engine for Real-Time Ads Retrieval

広告を表すID（SID）の候補を生成する途中で、その要求の配信条件を確認する。著者の評価では、最後に広告ごとの条件確認を通過した割合が23.55%から40.42%へ上がった。候補数を固定した生成処理のP99遅延は197.7 msから17.8 msへ短縮したが、配信条件の確認（GTM）を含むモデル全体のP99遅延53.6 msは別の条件で測った値である。

公開ページ: https://mixidota2.github.io/paper-lab/papers/grace-meta-ads-gtm-serving.html

## 実行

```bash
uv run papers/grace-meta-ads-gtm-serving/run.py
```

Python標準ライブラリだけを使う。`lab.yaml` と `method.md` が解説の原本、`run.py` が最小実験、`results.json` が出力、`mapping.md` が原典との対応。HTMLは `uv run paper-lab build` で生成する。

## 検証範囲

Mechanism PARTIAL。人工4要求で、適格広告を持つprefixがOR検査を通ることはCONFIRMED。属性相関の偽陽性、Bloomの偽陽性、同一beamの枠再配分を実行した。

Performance / Scaling / Production applicability NOT TESTED。GH200 kernel、KV cache、production targeting全条件、実pass率、広告A/Bは未実行。CPUの4広告を23.55→40.42%の再現とは呼ばない。

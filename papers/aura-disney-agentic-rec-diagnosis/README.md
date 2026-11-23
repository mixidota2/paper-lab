# AURA: Agentic Diagnosis and Refinement for Production Recommender Systems at Scale

著者らはDisneyのサービスAとBで、それぞれ約10万件の利用セッションを使って推薦の失敗を診断した。診断など各工程の出力を25項目の基準で評価したところ、基準を満たした項目はサービスAで15から23、サービスBで17から24に増えた。これは診断などの出力に対する評価で、推薦の順位が改善した件数ではない。実際にジャンル情報を使った修正案をオフラインで試しても、対象のセッションで順位の改善は確認できなかった。

公開ページ: https://mixidota2.github.io/paper-lab/papers/aura-disney-agentic-rec-diagnosis.html

## 実行

```bash
uv run papers/aura-disney-agentic-rec-diagnosis/run.py
```

Pythonの標準ライブラリだけで実行できる。解説は `lab.yaml` と `method.md`、原論文との対応は `mapping.md` にある。`run.py` が小実験を実行し、`results.json` に結果を保存する。公開ページは `uv run paper-lab build` で生成する。

## 検証範囲

仕組みの一部を確認した（Mechanism PARTIAL）。人工データでは、出現頻度が低くても残す分類を選び、参照先が存在するかを調べた。架空の参照を退けることは確認済み（CONFIRMED）。25項目の評価結果が上がったのは著者の報告で、Labでは確かめていない（NOT TESTED）。

性能、規模を拡大した場合の挙動、本番適用性は未検証（Performance / Scaling / Production applicability NOT TESTED）。セッションごとの判定、因果推論、モデル間での判定の一致、実際のランキングモデルの学習、A/Bテストは行っていない。提示メモの「出荷を拒否」は、今回の結果からは言えない。論文にあるジャンルの修正案は、効果が確認されていない候補のままである。著者らが報告した自動化の範囲は、エンジニアが確認するプルリクエストの作成までである。

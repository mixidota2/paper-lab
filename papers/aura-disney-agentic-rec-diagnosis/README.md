# AURA: Agentic Diagnosis and Refinement for Production Recommender Systems at Scale

著者らはDisneyのサービスAとBで、それぞれ約10万件の利用セッションを使って推薦の失敗を診断した。診断など各工程の出力を25項目の基準で評価したところ、基準を満たした項目はサービスAで15から23、サービスBで17から24に増えた。これは診断などの出力に対する評価で、推薦の順位が改善した件数ではない。実際にジャンル情報を使った修正案をオフラインで試しても、対象のセッションで順位の改善は確認できなかった。

公開ページ：https://mixidota2.github.io/paper-lab/papers/aura-disney-agentic-rec-diagnosis.html

## 合成例を実行する

配布した `run.py` を保存し、同じフォルダで `python run.py` を実行します。Pythonの標準ライブラリだけで動き、同じフォルダに `results.json` が出力されます。リポジトリでは `uv run papers/aura-disney-agentic-rec-diagnosis/run.py` でも実行できます。

論文の仕組みは `lab.yaml` と `method.md`、論文と合成例の対応は `mapping.md` にあります。リポジトリでは `uv run paper-lab build` でページを生成できます。

## Labで確かめた範囲

この例では、件数が少なくても安全上の問題として残す分類を選び、入力にないセッションIDやファイル名を含む診断を退けました。仕組みの一部を確認した結果です（Mechanism PARTIAL）。参照先の内容が診断の根拠になるかは調べていません。

Labは、実際の視聴セッションを判定したり、推薦モデルを学習させたりしていません。診断などの出力が満たした評価項目の増加も著者の報告です。ジャンルの修正案は、効果が確認されていない候補のままです。著者が報告した修正作業の自動化は、技術者が確認するプルリクエストを作るところまでです。

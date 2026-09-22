# AURA: Agentic Diagnosis and Refinement for Production Recommender Systems at Scale

Disneyの2 platformで約10万sessionずつを診断。25項目rubricは15→23、17→24へ改善したが、genre修正の順位改善は未実証。診断と出荷判断を切り離す。

公開ページ: https://mixidota2.github.io/paper-lab/papers/aura-disney-agentic-rec-diagnosis.html

## 実行

```bash
uv run papers/aura-disney-agentic-rec-diagnosis/run.py
```

Python標準ライブラリだけを使う。`lab.yaml` と `method.md` が解説の原本、`run.py` が最小実験、`results.json` が出力、`mapping.md` が原典との対応。HTMLは `uv run paper-lab build` で生成する。

## 検証範囲

Mechanism PARTIAL。低頻度category保持と参照の存在確認を人工入力で実行した。架空参照の拒否はCONFIRMED。診断品質のrubric上昇は著者報告でありLabではNOT TESTED。

Performance / Scaling / Production applicability NOT TESTED。session判定、因果推論、LLM間一致、実rankerの学習、A/Bを実行していない。提示メモの「出荷を拒否」は慎重に読む必要がある。原典は修正を未実証のopen candidateとし、現行システムの自動化範囲はengineer-reviewed PRまでである。

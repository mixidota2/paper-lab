# Original Paper / Official Code Mapping

一次資料: [SIDScope: A Diagnostic Resource for Semantic-ID Interfaces in Generative Recommendation](https://arxiv.org/html/2608.18779v1)。本文・実験・限界・付録を確認（2026-09-21）。キャッシュは `/tmp/research-2026-09-21/2608.18779.html`。HTML SHA-256: `8043cc1a9924d9a3fd53d1d786c74d17dc91844fbd59550df933fb87c5c16fa8`。

| 原典 | Labの対応 | 意図した省略・境界 |
| --- | --- | --- |
| §3.2 / D1,D2,D5 | diagnose | Gini・popularity D4は省略 |
| §3.2 / D3 | weighted_prefix_alignment | 入力pairを使用。公式近傍抽出は省略 |
| §6.3 / D6 | previous / code_churn | checkpoint適応は未検証 |
| §5 / D7 | trace | 最小のvalid/ambiguous/target会計のみ |

公式コード: [https://github.com/jdding/sidscope/tree/v1.0.1](https://github.com/jdding/sidscope/tree/v1.0.1)。v1.0.1を取得して確認。

## 公式コードの実行確認

`uv run --project /tmp/research-2026-09-21/SIDscope-1.0.1 /tmp/research-2026-09-21/SIDscope-1.0.1/examples/run_reviewer_quickstart.py` を実行しpreflight passed、D1–D5出力を確認。12 itemの公開quickstart入力であり、本番catalogではない。

独立実装のleaf数11、D2=2/12、D5=1/12、prefix数3/6/11が公式と一致。公式D1 entropyは各level単独、Labはprefix entropyなので、depth 2以降のentropyを同値比較しない。D3の公式近傍抽出は再実装していない。

| 公式 v1.0.1 | Lab |
| --- | --- |
| `src/sidinspector/metrics.py::collision` | `diagnose` のcollision_item_rate |
| `metrics.py::deployment_cost` | unique_leaves / duplicate_SID_rate / active_prefixes |
| `metrics.py::alignment` | 入力済みpairに対する部分実装 |
| `src/sidinspector/d7_trace.py` | `trace` のvalid/ambiguous/unique判定だけ |

release archive SHA-256: `852f79c01075708fa0b9161bd686e31a7dc3a37ff7ef3d1b0625c5ed5b39a525`。入力CSV SHA-256: `5ada9e4f9782dc12cb931fd54af86ac59fc78b65101d789d99b0fc984321dcaf`。公式実行の記録は `official-check.json`、入力例のMIT licenseは `NOTICE.txt`。

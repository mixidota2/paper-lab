# 原論文・公式コード対応

| 論文箇所 | 最小成果物 | 公式コード |
| --- | --- | --- |
| §3.1.1 Masked Action Modeling（vs interleaving） | `run.py` の系列長比較 | 非公開 |
| §3.3.3 KV-cache sharing across stages | `run.py` の encode-once vs twice | 非公開（Triton / CUDA IPC） |
| §4.1 Table 1 Hit@3 / Recall@10 | *未実装* | n/a |
| §4.2 Table 2–3 serving latency / QPS | 相対単位の玩具のみ | n/a |
| §5 Online A/B (BMI, Notifications) | *未実装 — NOT TESTED* | n/a |

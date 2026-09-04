"""Toy serving/sequence cost: history encode once vs twice; MAM vs interleaved length.

Illuminates KV-cache reuse and Masked Action Modeling length — not online BMI lifts.
"""
from __future__ import annotations

import json
from pathlib import Path

# Proxy FLOPs: attention ~ n^2 for history prefill; candidates add n*k (no cand-cand)
HISTORY_N = 992
CANDIDATES_K = 656
LAYERS = 12
D_MODEL = 64  # toy width for relative units


def attn_flops(seq_q: int, seq_kv: int) -> float:
    """Rough matmul units for QK^T / AV over layers (relative, not hardware-accurate)."""
    return LAYERS * seq_q * seq_kv * D_MODEL


def mam_seq_len(history: int, candidates: int) -> int:
    """Non-interleaved: history + candidates (actions on feature axis, not tokens)."""
    return history + candidates


def interleaved_seq_len(history: int, candidates: int) -> int:
    """HSTU-style: item/action interleaving roughly doubles history tokens."""
    return history * 2 + candidates * 2


def main() -> dict:
    # Separate deploy: encode history in retrieval, encode again in ranking
    hist_cost = attn_flops(HISTORY_N, HISTORY_N)
    rank_from_scratch = hist_cost + attn_flops(CANDIDATES_K, HISTORY_N + CANDIDATES_K)
    separate_total = hist_cost + rank_from_scratch

    # KV reuse: ranking only pays candidate→history attention
    rank_with_kv = attn_flops(CANDIDATES_K, HISTORY_N)
    unified_total = hist_cost + rank_with_kv

    mam_len = mam_seq_len(HISTORY_N, CANDIDATES_K)
    interleave_len = interleaved_seq_len(HISTORY_N, CANDIDATES_K)

    mam_train_attn = attn_flops(mam_len, mam_len)  # upper bound before sparsity
    # Paper: candidates blocked from each other → O(n^2 + n k)
    mam_sparse = attn_flops(HISTORY_N, HISTORY_N) + attn_flops(CANDIDATES_K, HISTORY_N)
    interleave_attn = attn_flops(interleave_len, interleave_len)

    experiments = [
        {
            "name": "toy_kv_reuse_serving",
            "dataset": f"synthetic_n{HISTORY_N}_k{CANDIDATES_K}",
            "n": 1,
            "seed": 0,
            "metrics": {
                "history_prefill_units": round(hist_cost, 1),
                "separate_deploy_total_units": round(separate_total, 1),
                "kv_reuse_total_units": round(unified_total, 1),
                "speedup_vs_separate": round(separate_total / unified_total, 3),
                "ranking_marginal_ratio": round(rank_with_kv / hist_cost, 3),
            },
        },
        {
            "name": "toy_mam_vs_interleave_length",
            "dataset": f"synthetic_n{HISTORY_N}_k{CANDIDATES_K}",
            "n": 1,
            "seed": 0,
            "metrics": {
                "mam_sequence_length": mam_len,
                "interleaved_sequence_length": interleave_len,
                "length_ratio_interleave_over_mam": round(interleave_len / mam_len, 3),
                "mam_sparse_attn_units": round(mam_sparse, 1),
                "interleave_dense_attn_units": round(interleave_attn, 1),
                "attn_ratio_interleave_over_mam_sparse": round(
                    interleave_attn / mam_sparse, 3
                ),
            },
        },
    ]
    payload = {
        "note": (
            "Relative FLOP/sequence-length toy only. Illustrates why history encode-once "
            "(KV reuse) and non-interleaved MAM matter for serving/context. Does not "
            "reproduce offline Hit@3, online BMI/push lifts, or production QPS."
        ),
        "fictional": False,
        "toy": True,
        "paper_claims_not_tested": [
            "offline Hit@3 +14.8%",
            "online BMI saves +0.95%",
            "push opens +0.91%",
            "e2e latency -11.1% / QPS +63.6%",
            "L2 fine ranker replacement",
        ],
        "summary": {
            "kv_reuse_speedup_vs_separate": experiments[0]["metrics"]["speedup_vs_separate"],
            "interleave_length_inflation": experiments[1]["metrics"][
                "length_ratio_interleave_over_mam"
            ],
        },
        "experiments": experiments,
    }
    out = Path(__file__).resolve().parent / "results.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return payload


if __name__ == "__main__":
    main()

"""Toy cost/grounding contrast: ANN/dot-product retrieval vs sequential SID generation.

Illuminates the paper's efficiency/grounding argument — not Amazon R@K or production NE.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

SEED = 7
N_QUERIES = 500
CATALOG = 10_000
TOP_K = 10
# Generative SID: decode L tokens then map to item; each step can miss the codebook
SID_LEN = 4
GROUNDING_MISS_P = 0.08  # per-token codebook miss → invalid item path
# Relative flop proxies (arbitrary units): encode once vs decode steps
USER_ENCODE_COST = 12.0
ITEM_PRECOMPUTE_AMORTIZED = 0.002  # already indexed
ANN_PROBE_COST = 0.4
DECODE_STEP_COST = 3.5


def ann_retrieve(rng: random.Random) -> dict:
    """User encode once + ANN over precomputed item vectors."""
    cost = USER_ENCODE_COST + ANN_PROBE_COST * math.log2(CATALOG)
    # Dot-product over indexed vectors: always grounded to real item IDs
    hit = int(rng.random() < 0.42)  # synthetic relevance rate
    return {
        "cost": cost,
        "latency_steps": 1,
        "grounding_miss": 0,
        "hit_at_k": hit,
    }


def generative_sid(rng: random.Random) -> dict:
    """Autoregressive semantic-ID decode + post-hoc token→item mapping."""
    cost = USER_ENCODE_COST
    miss = 0
    for _ in range(SID_LEN):
        cost += DECODE_STEP_COST
        if rng.random() < GROUNDING_MISS_P:
            miss = 1
            break
    # If any token misses codebook, candidate is invalid / needs repair
    if miss:
        hit = 0
        # repair attempt: extra decode budget
        cost += DECODE_STEP_COST * 2
    else:
        hit = int(rng.random() < 0.45)
    return {
        "cost": cost,
        "latency_steps": SID_LEN + (2 if miss else 0),
        "grounding_miss": miss,
        "hit_at_k": hit,
    }


def main() -> dict:
    rng = random.Random(SEED)
    ann_rows = [ann_retrieve(rng) for _ in range(N_QUERIES)]
    gen_rows = [generative_sid(rng) for _ in range(N_QUERIES)]

    def agg(rows: list[dict]) -> dict:
        n = len(rows)
        return {
            "mean_cost": round(sum(r["cost"] for r in rows) / n, 3),
            "mean_latency_steps": round(sum(r["latency_steps"] for r in rows) / n, 3),
            "grounding_miss_rate": round(sum(r["grounding_miss"] for r in rows) / n, 3),
            "hit_at_10": round(sum(r["hit_at_k"] for r in rows) / n, 3),
        }

    ann_m = agg(ann_rows)
    gen_m = agg(gen_rows)
    experiments = [
        {
            "name": "toy_ann_two_tower",
            "dataset": f"synthetic_catalog_n{CATALOG}",
            "n": N_QUERIES,
            "seed": SEED,
            "metrics": ann_m,
        },
        {
            "name": "toy_generative_sid_decode",
            "dataset": f"synthetic_catalog_n{CATALOG}",
            "n": N_QUERIES,
            "seed": SEED,
            "sid_len": SID_LEN,
            "metrics": gen_m,
        },
    ]
    payload = {
        "note": (
            "Synthetic catalog simulation only. Contrasts serving cost shape and "
            "grounding miss rate for ANN/dot-product vs sequential SID decode. "
            "Does not reproduce Amazon R@10, CE SOTA, or production NE vs DLRM."
        ),
        "fictional": False,
        "toy": True,
        "paper_claims_not_tested": [
            "Amazon Beauty/Sports/Toys R@10 / NDCG",
            "CE yes/no+NTP teacher quality",
            "CE2TT distillation gains",
            "production NE parity at 0.5% data",
            "staleness resilience vs DLRM",
        ],
        "summary": {
            "cost_ratio_gen_over_ann": round(gen_m["mean_cost"] / ann_m["mean_cost"], 3),
            "latency_steps_ratio": round(
                gen_m["mean_latency_steps"] / ann_m["mean_latency_steps"], 3
            ),
            "grounding_miss_ann": ann_m["grounding_miss_rate"],
            "grounding_miss_gen": gen_m["grounding_miss_rate"],
        },
        "experiments": experiments,
    }
    out = Path(__file__).resolve().parent / "results.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return payload


if __name__ == "__main__":
    main()

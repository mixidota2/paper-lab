"""Toy unified recommender: counts history recomputation and cache reuse."""
from __future__ import annotations

import json
import random
from pathlib import Path


def score(history: list[int], item: int) -> float:
    return sum(1 for x in history[-5:] if x % 7 == item % 7) + (item % 3) / 10


def evaluate(unified: bool) -> dict[str, float | int]:
    rng = random.Random(20260904)
    hits = recomputes = cache_hits = 0
    for _ in range(80):
        history = [rng.randrange(50) for _ in range(16)]
        target = history[-1] % 7 + 35
        candidates = [target] + [rng.randrange(50) for _ in range(9)]
        recomputes += 1  # retrieval history prefill
        if unified:
            cache_hits += 1
        else:
            recomputes += 1  # independent ranker repeats the prefill
        ranked = sorted(candidates, key=lambda item: score(history, item), reverse=True)
        hits += target in ranked[:3]
    return {"hit_at_3": round(hits / 80, 3), "history_prefills": recomputes, "cache_hits": cache_hits, "simulated_work_units": recomputes * 16 + 80 * 10}


if __name__ == "__main__":
    output = {"note": "合成履歴で、同じランキング規則を使いながら履歴 prefill の重複だけを数える玩具実験。Pinterest の GPU 遅延やオンライン指標は再現していない。", "experiments": [{"name": "分離 cascade と KV 再利用", "dataset": "synthetic 80 sessions", "n": 80, "seed": 20260904, "metrics": {"separate_retrieval_ranking": evaluate(False), "unified_cache_reuse": evaluate(True)}}], "boundary": "共有状態が同じ候補ランキングを保ったまま再計算量を減らせることの例示に限る。"}
    Path(__file__).with_name("results.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))

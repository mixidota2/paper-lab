"""Tiny synthetic retrieval comparison; it is not Meta's production system."""
from __future__ import annotations

import json
import random
import time
from pathlib import Path


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def run() -> dict:
    rng = random.Random(20260904)
    catalog = [[rng.uniform(-1, 1) for _ in range(12)] for _ in range(160)]
    queries = [(catalog[i][:], i) for i in range(40)]
    generated_ok = 0
    start = time.perf_counter()
    for vector, truth in queries:
        # A deliberately sequential semantic-ID decoder: each token scans a vocabulary.
        token_scores = [sum(dot(vector, item) for item in catalog) + i for i in range(32)]
        decoded = (int(max(range(32), key=token_scores.__getitem__)) * 5 + truth % 5) % len(catalog)
        generated_ok += decoded == truth
    generative_ms = (time.perf_counter() - start) * 1000
    start = time.perf_counter()
    ann_ok = 0
    for vector, truth in queries:
        best = max(range(len(catalog)), key=lambda i: dot(vector, catalog[i]))
        ann_ok += best == truth
    two_tower_ms = (time.perf_counter() - start) * 1000
    metrics = {
        "generative_style_decode": {"recall_at_1": round(generated_ok / len(queries), 3), "elapsed_ms": round(generative_ms, 3), "grounding_failures": len(queries) - generated_ok},
        "two_tower_exact_ann": {"recall_at_1": round(ann_ok / len(queries), 3), "elapsed_ms": round(two_tower_ms, 3), "grounding_failures": 0},
    }
    return {"note": "合成ベクトルと意図的に壊れやすい逐次 ID デコードの比較。ANN ライブラリ、LLM、Meta の NE は使わない。", "experiments": [{"name": "逐次 ID デコードと因子化検索", "dataset": "synthetic catalog", "n": 40, "seed": 20260904, "metrics": metrics}], "boundary": "逐次デコードの grounding と計算経路のトレードオフを可視化するだけで、実サービスの性能比較ではない。"}


if __name__ == "__main__":
    output = run()
    Path(__file__).with_name("results.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))

"""真の改善がない候補を、同じ乱数列で二つの規則にかける合成例。
追加測定の条件はLabが決めたもので、監査対象の実装ではない。
"""
import json
import math
import random
import statistics
from pathlib import Path


def simulate(seed, gated, rounds=100):
    rng = random.Random(seed)
    trunk, reported, true_value = 0, 0.0, 0.0
    path, kept = [], 0
    for t in range(rounds):
        # 候補を採択しても、真の改善量はすべてゼロのまま。
        offline_delta = rng.gauss(0, 0.01)
        repeats = [rng.gauss(0, 0.01) for _ in range(25)]
        audit_delta = rng.gauss(0, 0.01)
        mean = statistics.mean(repeats)
        se = statistics.stdev(repeats)/math.sqrt(len(repeats))
        # 初回の条件に、追加測定の平均と標準誤差を使う条件を重ねる。
        promote = offline_delta > 0.001
        if gated:
            promote = promote and mean > max(0.001, 3.5*se)
        previous = trunk
        if promote:
            trunk = t+1
            kept += 1
            reported += offline_delta
        path.append({"round": t+1, "parent": previous, "trunk": trunk, "keep": promote, "observed_delta": round(offline_delta, 6), "reported_cumulative_gain": round(reported, 6), "true_gain": true_value, "fresh_audit_delta": round(audit_delta, 6)})
    return {"keeps": kept, "reported_gain": reported, "true_gain": true_value, "path": path}


def experiment():
    metrics = {}
    for label, gated in [("one_run_keep", False), ("repeat_evidence_gate", True)]:
        runs = [simulate(seed, gated) for seed in range(200)]
        metrics[label] = {"mean_keeps": statistics.mean(r["keeps"] for r in runs), "mean_reported_gain": round(statistics.mean(r["reported_gain"] for r in runs), 6), "true_gain": 0, "runs_with_false_keep": sum(r["keeps"] > 0 for r in runs)}
    return {"note": "全候補の真の改善はゼロです。採択した測定差の合計が増える場合を示します。論文のAUCや実際のAutoLRの性能は再現していません。", "experiments": [{"name": "同じ測定値の列で採択規則を比べる", "seed": "0..199", "n": {"runs": 200, "rounds": 100, "repeats": 25}, "metrics": metrics}], "paths": {"one_run_keep": simulate(9, False)["path"], "repeat_evidence_gate": simulate(9, True)["path"]}}


def compute():
    result = experiment()
    result["verification"] = {
        "mechanism": "PARTIAL", "performance": "NOT TESTED",
        "scaling": "NOT TESTED", "production_applicability": "NOT TESTED",
    }
    return result


if __name__ == "__main__":
    Path(__file__).with_name("results.json").write_text(json.dumps(compute(), ensure_ascii=False, indent=2)+"\n")

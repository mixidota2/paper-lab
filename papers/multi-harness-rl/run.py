"""Frozen trajectories and credit grouping. No policy update or LLM API."""
import json
import math
from pathlib import Path


def execute(interface, trajectory):
    # Same underlying task: return two. Interface accepts a different syntax.
    expected = {"A": "return 2", "B": '{"answer":2}', "held_out": "<answer>2</answer>"}
    return int(trajectory == expected[interface])


def advantages(rewards):
    mean = sum(rewards)/len(rewards)
    sd = math.sqrt(sum((r-mean)**2 for r in rewards)/len(rewards))
    return [(r-mean)/(sd+1e-8) for r in rewards]


def experiment():
    traces = {"A": ["return 2"]*4, "B": ['{"answer":2}', "return 2", "return 3", "return 4"]}
    rewards = {h: [execute(h, t) for t in ts] for h, ts in traces.items()}
    within = {h: advantages(rs) for h, rs in rewards.items()}
    cross = advantages(rewards["A"]+rewards["B"])
    records = []
    for hi, (h, ts) in enumerate(traces.items()):
        for j, t in enumerate(ts):
            records.append({"harness": h, "trace": t, "reward": rewards[h][j], "within": round(within[h][j], 6), "cross": round(cross[hi*4+j], 6)})
    scores = {h: sum(execute(h, t) for ts in traces.values() for t in ts)/8 for h in ["A", "B", "held_out"]}
    return {"note": "合成インターフェースの固定軌跡。勾配係数のみ計算し、方策は更新しない。未見スコア不変は設計上の対照であり、論文の帰無結果の再現ではない。", "experiments": [{"name": "評価インターフェースを交換", "metrics": scores}, {"name": "非ゼロのadvantageを持つ軌跡", "metrics": {"Within": sum(r["within"] != 0 for r in records), "Cross": sum(r["cross"] != 0 for r in records)}}], "trajectories": records, "held_out_before": scores["held_out"], "held_out_after_credit_only": scores["held_out"]}


def compute():
    result = experiment()
    result["verification"] = {
        "mechanism": "PARTIAL", "performance": "NOT TESTED",
        "scaling": "NOT TESTED", "production_applicability": "NOT TESTED",
    }
    return result


if __name__ == "__main__":
    Path(__file__).with_name("results.json").write_text(json.dumps(compute(), ensure_ascii=False, indent=2)+"\n")

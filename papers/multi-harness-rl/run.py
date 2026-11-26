"""固定した出力の報酬を二つの比較群で標準化する。方策は更新せず、LLMも呼び出さない。"""
import json
import math
from pathlib import Path


def execute(interface, trajectory):
    # どの形式でも課題は値2を返すこと。正解とする書き方だけが異なる。
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
    return {"note": "Labは同じ8件の出力で更新係数を計算しました。方策を更新しないので、新しい形式の採点結果は前後で同じです。論文の学習後の結果は再現していません。", "experiments": [{"name": "出力は固定し、採点する形式を変える", "metrics": scores}, {"name": "更新係数が0ではない記録の件数", "metrics": {"Within": sum(r["within"] != 0 for r in records), "Cross": sum(r["cross"] != 0 for r in records)}}], "trajectories": records, "held_out_before": scores["held_out"], "held_out_after_credit_only": scores["held_out"]}


def compute():
    result = experiment()
    result["verification"] = {
        "mechanism": "PARTIAL", "performance": "NOT TESTED",
        "scaling": "NOT TESTED", "production_applicability": "NOT TESTED",
    }
    return result


if __name__ == "__main__":
    Path(__file__).with_name("results.json").write_text(json.dumps(compute(), ensure_ascii=False, indent=2)+"\n")

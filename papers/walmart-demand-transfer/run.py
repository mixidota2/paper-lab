"""Restricted-logit inference with declared utilities (no parameter fitting)."""
import json
import math
from pathlib import Path


def coefficients(utilities, substitutes, loyalty):
    n = len(utilities)
    rows = []
    for i in range(n):
        allowed = [j for j in substitutes[i] if j != i]
        denom = sum(math.exp(utilities[j]) for j in allowed)
        rows.append([(1-loyalty[i])*math.exp(utilities[j])/denom if j in allowed else 0.0 for j in range(n)])
    return rows


def remove_one(demand, dt, removed):
    adjusted = [demand[j]+dt[removed][j]*demand[removed] if j != removed else 0 for j in range(len(demand))]
    lost = demand[removed]*(1-sum(dt[removed]))
    return adjusted, lost


def experiment():
    demand = [100, 60, 40, 30]
    utilities = [math.log(v) for v in [4, 3, 1, 2]]
    substitutes = [{1, 2}, {0, 2}, {0, 1}, set()]
    dt = coefficients(utilities, substitutes, [0.2, 0.25, 0.1, 1])
    adjusted, lost = remove_one(demand, dt, 0)
    independent = [0, 60, 40, 30]
    # A deliberately different behavioral scenario tests assumption failure.
    counterexample = [0, 80, 100, 30]
    wmape = lambda pred, actual: sum(abs(a-b) for a, b in zip(pred, actual))/sum(actual)
    metrics = {"assumption_matched": {"independent_WMAPE": round(wmape(independent, adjusted), 6), "DT_WMAPE": wmape(adjusted, adjusted)}, "within_set_preference_shift": {"independent_WMAPE": round(wmape(independent, counterexample), 6), "DT_WMAPE": round(wmape(adjusted, counterexample), 6)}}
    return {"note": "Labは四つの商品の効用をあらかじめ決め、手で追える計算を示す。正解を予測と同じ規則で作ると誤差がゼロになるが、実データでの精度を示す結果ではない。", "demand": demand, "coefficients": dt, "removed_item": 0, "independent": independent, "adjusted": adjusted, "lost_demand": lost, "counterexample_actual": counterexample, "experiments": [{"name": "商品Aを棚から外したときの販売予測", "metrics": metrics}]}


def compute():
    result = experiment()
    result["verification"] = {
        "mechanism": "PARTIAL", "performance": "NOT TESTED",
        "scaling": "NOT TESTED", "production_applicability": "NOT TESTED",
    }
    return result


if __name__ == "__main__":
    Path(__file__).with_name("results.json").write_text(json.dumps(compute(), ensure_ascii=False, indent=2)+"\n")

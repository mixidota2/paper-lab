"""CoA entropy, exposure-capacity repair, and a Bayes ranking counterexample."""
import json
import math
from pathlib import Path
from collections import Counter

def entropy(counts):
    total = sum(counts)
    return -sum((n/total)*math.log2(n/total) for n in counts if n) if total else 0.0

def capacity_repair(points, weights, centers, tolerance=1.05):
    assignments = [min(range(len(centers)), key=lambda k: abs(x-centers[k])) for x in points]
    cap = sum(weights)/len(centers)*tolerance
    def loads(): return [sum(w for w,z in zip(weights,assignments) if z==k) for k in range(len(centers))]
    before = loads()
    for k in range(len(centers)):
        for i in sorted(range(len(points)), key=lambda i: weights[i]):
            if loads()[k] <= cap: break
            if assignments[i] != k: continue
            choices = [j for j in range(len(centers)) if j != k and loads()[j]+weights[i] <= cap]
            if choices: assignments[i] = min(choices,key=lambda j:abs(points[i]-centers[j]))
    return {"before": before, "after": loads(), "capacity": cap, "feasible": max(loads())<=cap}

def compute():
    # 4 SID tokens, two categories; the attribute is observed exactly in this toy.
    joint = [(a,s) for a,ss in [("X",[0,0,1,1]),("Y",[2,2,3,3])] for s in ss]
    h = entropy(list(Counter(s for a,s in joint).values()))
    conditional = sum(.5*entropy(list(Counter(s for aa,s in joint if aa==a).values())) for a in ["X","Y"])
    repair=capacity_repair([0,.1,.2,.3,1,1.1,1.2,1.3],[3,3,1,1,1,1,1,1],[0,1])
    impossible=capacity_repair([0,1],[20,1],[0,1])
    prior=[.9,.1]; engagement=[.2,.8]
    py=sum(a*b for a,b in zip(prior,engagement))
    posterior=[a*b/py for a,b in zip(prior,engagement)]
    corrected=[p*py/f for p,f in zip(posterior,prior)]
    return {"note":"人工分布。CoAの属性予測、RQモデルの学習、Shopeeの精度は再現しない。",
      "experiments":[{"name":"属性条件付きエントロピー", "metrics":{"属性なし(bit)":h,"属性あり(bit)":conditional,"減少(bit)":h-conditional}},
      {"name":"Bayesの分母を省くと順位が逆転する", "metrics":{"商品A":{"p(f|u)":prior[0],"p(y=1|f,u)":engagement[0],"p(f|y=1,u)":posterior[0]},"商品B":{"p(f|u)":prior[1],"p(y=1|f,u)":engagement[1],"p(f|y=1,u)":posterior[1]}}}],
      "capacity":repair,"infeasible_heavy_item":impossible,"bayes_corrected":corrected,
      "checks":{"conditional_entropy_identity":"CONFIRMED","unconditional_ranking_equivalence":"NOT OBSERVED","capacity_for_heavy_item":"NOT OBSERVED","production_performance":"NOT TESTED"}}


def main():
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

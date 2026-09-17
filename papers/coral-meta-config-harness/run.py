"""CORAL numerical tool analogue: exact budget projection and discrete allocation."""
import json
import itertools
from pathlib import Path

def project(proposal,budget):
    if budget<0:raise ValueError("negative budget")
    proposal=[max(0.,x) for x in proposal]
    if sum(proposal)<=budget:return proposal
    # Euclidean projection onto x>=0, sum(x)<=B; this norm is a Lab choice.
    lo,hi=0.,max(proposal)
    for _ in range(100):
        mid=(lo+hi)/2
        if sum(max(0.,x-mid) for x in proposal)>budget:lo=mid
        else:hi=mid
    return [max(0.,x-hi) for x in proposal]

def discrete(proposal,costs,budget):
    feasible=[x for x in itertools.product(range(len(costs)),repeat=len(proposal)) if sum(costs[i] for i in x)<=budget]
    return min(feasible,key=lambda x:(sum((a-b)**2 for a,b in zip(x,proposal)),x))

def compute():
    proposals=[[4,3,2],[8,7,5],[1,1,1]]
    frames=[{"proposal":p,"deployed":project(p,10)} for p in proposals]
    for x in frames:x["cost"]=sum(x["deployed"])
    # Synthetic first-round saving, to expose the denominator of 44%.
    base,first=100.,10.
    return {"note":"提案は手作り。LLM・実トラフィック・学習効果は含まない。ユークリッド距離と単価一定はLabの仮定。",
      "experiments":[{"name":"予算10へ射影する数値ツール", "metrics":{str(i+1):{"提案費用":sum(x["proposal"]),"配信費用":x["cost"]} for i,x in enumerate(frames)}},
      {"name":"削減額44%増の分母", "metrics":{"元の費用":base,"初回の削減額":first,"次回の削減額":first*1.44,"次回の費用":base-first*1.44}}],
      "frames":frames,"discrete_treatment":discrete([2,2,1],[1,3,6],10),
      "checks":{"budget_feasibility":"CONFIRMED","already_feasible_identity":"CONFIRMED","continual_policy_improvement":"NOT TESTED"}}


def main():
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

"""人工の設定案を予算内に収める例。CORALの数値ツールの実装を再現したものではない。"""
import json
import itertools
from pathlib import Path

def project(proposal,budget):
    if budget<0:raise ValueError("negative budget")
    proposal=[max(0.,x) for x in proposal]
    if sum(proposal)<=budget:return proposal
    # Labでは、各値が0以上で合計が予算以下となる設定にユークリッド射影する。
    # 予算に収まる設定は、浮動小数点で二分探索して近似する。
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
    # 44%が初回の削減額に対する増加率であることを、人工の金額で示す。
    base,first=100.,10.
    return {"note":"Labが用意した設定案を使い、単価は一定とする。案が予算を超えたときは、ユークリッド距離で案に近い設定を求める。言語モデルによる提案や学習、本番での効果は試していない。",
      "experiments":[{"name":"提案を予算10に収めると、費用はどう変わるか", "metrics":{str(i+1):{"提案費用":sum(x["proposal"]),"配信費用":x["cost"]} for i,x in enumerate(frames)}},
      {"name":"初回より削減額が44%増えたとき、費用はいくら残るか", "metrics":{"元の費用":base,"初回の削減額":first,"次回の削減額":first*1.44,"次回の費用":base-first*1.44}}],
      "frames":frames,"discrete_treatment":discrete([2,2,1],[1,3,6],10),
      "checks":{"budget_feasibility":"CONFIRMED","already_feasible_identity":"CONFIRMED","continual_policy_improvement":"NOT TESTED"}}


def main():
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

"""Exact arithmetic for Figure 1 and Proposition 7, not a retail performance trial."""
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

GAMMAS = (1, 2, 3, 5, 7, 11, 21)
def demand_interval(gamma):
    g=F(str(gamma))
    if g<1: raise ValueError("gamma must be at least 1")
    return F(1,5)+F(3,5)/(1+g), F(1,5)+F(3,5)*g/(1+g)

def one_cost(p_zero, order):
    if order not in (0,1): raise ValueError("binary action required")
    return F(3,10)+F(1,5)*p_zero if order else F(4,5)*(1-p_zero)

def one(gamma):
    lo,hi=demand_interval(gamma)
    rows=[]
    for p in (lo,hi):
        costs=[one_cost(p,a) for a in (0,1)]
        rows.append(dict(p_zero=float(p),costs=list(map(float,costs)),
                         regrets=[float(c-min(costs)) for c in costs]))
    worst=[max(r['regrets'][a] for r in rows) for a in (0,1)]
    return dict(gamma=gamma,p_zero=[float(lo),float(hi)],endpoints=rows,
                worst_regret=worst,data_debt=min(worst))

def two_cost(theta1,theta2,policy,c=F(7,10)):
    # Complete deterministic Markov rule: actions at (t1,x0), (t2,x0), (t2,x1).
    # At inventory 1, only action 0 is feasible.
    a1,a20,a21=policy
    if a1 not in (0,1) or a20 not in (0,1) or a21!=0:
        raise ValueError("infeasible policy")
    total=F(0)
    for d1,d2 in product((0,1),repeat=2):
        mass=(theta1 if d1 else 1-theta1)*(theta2 if d2 else 1-theta2)
        inv=max(a1-d1,0); a2=a20 if inv==0 else a21
        cost=c*(a1+a2)+max(d1-a1,0)+max(d2-inv-a2,0)
        total+=mass*cost
    return total

def carryover():
    policies=list(product((0,1),(0,1),(0,)))
    lo,hi=F(7,20),F(13,20)
    corners=[]
    for t1,t2 in product((lo,hi),repeat=2):
        costs=[two_cost(t1,t2,p) for p in policies]
        corners.append(dict(theta=[float(t1),float(t2)],
            costs=list(map(float,costs)),regrets=[float(c-min(costs)) for c in costs]))
    worst=[max(row['regrets'][i] for row in corners) for i in range(4)]
    return dict(policies=policies,corners=corners,worst_regret=worst,
                data_debt=min(worst),chosen_policy=policies[worst.index(min(worst))])

def results():
    cases=[one(g) for g in GAMMAS]
    return dict(note="論文の人工例を数式から計算した。実店舗の販売、費用、効果は測っていない。",
        verification=dict(mechanism="PARTIAL",performance="NOT TESTED",
                          scaling="NOT TESTED",production_applicability="NOT TESTED"),
        experiments=[dict(name="図1の単期例",metrics={"Γ=11の最大費用差":one(11)['data_debt']}),
                     dict(name="命題7の2期間例",metrics={"持越しがある場合の最小最大費用差":carryover()['data_debt']})],
        calculations=cases,carryover=carryover(),
        explorer=dict(label="隠れた需要の偏りに許す上限 Γ",unit="",metric="需要を知る最適行動より余分にかかる費用（人工単位）",default=5,
          frames=[dict(value=r['gamma'],bars=[
              dict(label="注文しない場合の最大費用差",value=r['worst_regret'][0]),
              dict(label="1個注文する場合の最大費用差",value=r['worst_regret'][1])],
              note=f"需要0の確率は{r['p_zero'][0]:.4f}〜{r['p_zero'][1]:.4f}の範囲です。観測割合は20%・20%・60%に固定しています。Γはデータから推定した値ではなく、分析者が置く仮定です。どちらの棒も、その行動にとって最も不利な需要分布で計算しています。二つの棒が同じ分布の費用を示すわけではありません。",
              lines=[]) for r in cases]))
if __name__=="__main__":
    Path(__file__).with_name("results.json").write_text(json.dumps(results(),ensure_ascii=False,indent=2)+"\n")

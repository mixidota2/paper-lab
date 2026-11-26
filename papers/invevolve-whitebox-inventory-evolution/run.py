"""人工需要で発注量と費用差を計算する。言語モデルの学習や論文の追試は行わない。"""
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).parent

def order(gap, cap=4, alpha=0, kp=1, pic=False):
    target = math.floor(kp * gap + 0.5) if pic else gap
    return max(0, min(target, cap + alpha * gap))

def replay(demand, alpha, kp, pic):
    inventory, pipeline, total = 10.0, [4.0] * 3, 0.0
    for d in demand:
        inventory += pipeline.pop(0)
        q = order(max(0, 24 - inventory - sum(pipeline)), alpha=alpha, kp=kp, pic=pic)
        sold = min(inventory, d)
        inventory -= sold
        pipeline.append(q)
        total += inventory + 9 * (d - sold)
    return total / len(demand)

def main():
    rng = random.Random(930)
    paths = [[rng.randint(0, 10) for _ in range(60)] for _ in range(256)]
    policies = [('CBS',0,1,False),('Tilted-CBS',.25,1,False),('Tilted-PIC',.25,.65,True)]
    costs = {name:[replay(d,a,k,p) for d in paths] for name,a,k,p in policies}
    # CBS系は q <= gap。Tilted-PICは係数0.65の積を四捨五入するため、
    # gap=0.875で q=1 になるように、不足を最大0.5だけ超えることがある。
    # 初期の在庫と入荷予定の合計は22。入荷で合計は変わらず、販売で増えないので、
    # 発注後も24.5以下。終日在庫と売り逃しは同じ日に正にならないため、
    # 1日の費用は max(24.5, 9*10)=90 以下。区間向けの上限114は据え置く。
    bound, delta, comparisons = 114, .05, 2
    radius = bound * math.sqrt(2 * math.log(2 * comparisons / delta) / len(paths))
    rows=[]
    for name, *_ in policies:
        mean=sum(costs[name])/len(paths)
        gain=sum(b-c for b,c in zip(costs['CBS'],costs[name]))/len(paths)
        rad=0 if name=='CBS' else radius
        rows.append(dict(policy=name,cost=mean,gain=gain,radius=rad,lcb=gain-rad,ucb=gain+rad))
    frames=[]
    for alpha,kp in [(0,1),(.25,1),(.25,.65),(.6,.65),(.25,1.3)]:
        frames.append(dict(label=f'α={alpha} / Kp={kp}',alpha=alpha,kp=kp,curve=[dict(gap=g,cbs=order(g),tilted=order(g,alpha=alpha),pic=order(g,alpha=alpha,kp=kp,pic=True)) for g in range(31)]))
    assert all(order(g,alpha=0)==order(g) for g in range(31))
    assert all(order(g,alpha=.25,kp=1,pic=True)==order(g,alpha=.25) for g in range(31))
    assert all(0 <= c <= bound for cs in costs.values() for c in cs)
    out=dict(lab30='invevolve',scope='人工需要で発注量と費用差を計算し、固定の参照方策を置き換える条件を確かめる。論文の追試ではない。',seed=930,paths=256,days=60,lead_time=3,base_stock=24,base_cap=4,holding=1,penalty=9,bound=bound,delta=delta,comparisons=comparisons,replay=rows,frames=frames,checks={'alpha_zero_recovers_cbs':True,'integer_gap_kp_one_recovers_tilted':True,'bounded_cost':True},paper_reported={'synthetic':{'base_glm':13,'invevolve':25,'n':30},'cj':{'invevolve':20,'a3c':11,'e2e':16,'n':30,'cost_reduction_on_wins_pct':9.2},'stationary':{'tilted_cbs':[18,74,4],'tilted_pic':[41,47,8],'n':96,'tie_threshold_pct':2}},verification={'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'})
    (ROOT/'results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(rows,ensure_ascii=False,indent=2))

if __name__=='__main__': main()

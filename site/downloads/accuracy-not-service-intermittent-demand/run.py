"""Synthetic decision replay + normalization algebra, NOT Chronos inference/RUF."""
import json
import math
import random
from statistics import mean,pstdev
from pathlib import Path


def normalize(xs, nonzero=False):
    context = [x for x in xs if x > 0] if nonzero else xs
    center = mean(context) if context else 0
    scale = max(pstdev(context) if context else 0,1e-6)
    return [(x-center)/scale for x in xs], center, scale


def replay(orders, target, lead=2):
    stock = list(target)
    pipeline=[]; completed=0; inventories=[]
    for t,month in enumerate(orders):
        for due,receipt in pipeline:
            if due==t: stock=[a+b for a,b in zip(stock,receipt)]
        pipeline=[(d,r) for d,r in pipeline if d>t]
        for order in month:
            if all(a>=b for a,b in zip(stock,order)):
                stock=[a-b for a,b in zip(stock,order)];completed+=1
        inventories.append(sum(stock))
        position=[stock[i]+sum(r[i] for _,r in pipeline) for i in range(len(stock))]
        pipeline.append((t+lead,[max(0,s-p) for s,p in zip(target,position)]))
    return completed/sum(map(len,orders)),mean(inventories)


def main():
    rng=random.Random(22)
    history=[[rng.choice([0,0,0,0,2,5]) for _ in range(60)] for _ in range(4)]
    orders=[]
    for _ in range(36):
        month=[]
        for _ in range(4):
            order=[0]*4
            for i in rng.sample(range(4),2):order[i]=rng.choice([1,2,4])
            month.append(order)
        orders.append(month)
    actual=[[sum(o[i] for o in month) for month in orders] for i in range(4)]
    rows=[]
    for alpha in [.5,.75,1,1.25,1.5,2,3,4]:
        mu=[mean(x)*alpha for x in history]
        targets=[m*3+1.28155*pstdev(x)*math.sqrt(3) for m,x in zip(mu,history)]
        cofr,inventory=replay(orders,targets)
        mae=mean(abs(v-m) for x,m in zip(actual,mu) for v in x)
        rows.append({'alpha':alpha,'MAE':round(mae,6),'COFR':round(cofr,6),'inventory_units':round(inventory,6),'stock_target':round(sum(targets),6)})
    xs=[0,0,0,0,2,0,0,0,6,0]
    norms={}
    for name,nz in [('all',False),('positive',True)]:
        z,c,s=normalize(xs,nz)
        assert max(abs(v-(w*s+c)) for v,w in zip(xs,z))<1e-9
        norms[name]={'center':c,'scale':s,'normalized':z,'constant_z0_inverse':c}
    for edge in [[0,0],[0,2],[2,2]]:
        assert all(math.isfinite(v) for v in normalize(edge,True)[0])
    # More stock need not improve complete-order fill: an earlier large order consumes it.
    trap=[[[3],[1],[1]]]
    small=replay(trap,[2])[0];large=replay(trap,[3])[0]
    assert small>large
    out={'note':'固定seedの人工注文。論文38手法・RUF・Chronos-2の再現ではない。MAEを使用し論文MASEと区別。',
      'scope':{'normalization_roundtrip':'CONFIRMED','mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},
      'seed':22,'sweep':rows,'normalization':norms,'counterexample':{'stock2_COFR':small,'stock3_COFR':large},
      'experiments':[{'name':'同一144注文・補充方策で予測倍率を変更','metrics':{str(r['alpha']):{'MAE':r['MAE'],'COFR':r['COFR'],'inventory':r['inventory_units']} for r in rows}}]}
    from plot import render
    render(out)
    Path(__file__).with_name('results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');return out
if __name__=='__main__':main()

"""Trial/reorder scalarization with a trainable pairwise linear proxy.
Not CatBoost or a trained Transformer. Synthetic logits and distance are fixed inputs.
"""
import json, math, random
from pathlib import Path

def samples(seed,n):
    rng=random.Random(seed); rows=[]
    for _ in range(n):
        trial=rng.random()<.3
        # Candidate 0 is familiar; candidate 1 is a new store.
        h=rng.uniform(.2,1.4); distance=rng.uniform(-1,1)
        x=(h,distance,1.) # feature difference (new minus familiar)
        # Intent is partly unobserved: same feature can carry conflicting labels.
        y=1 if trial else -1
        rows.append((x,y,trial))
    return rows

def fit(rows,weight):
    w=[0.,0.,0.]
    for _ in range(300):
        g=[0.]*3; mass=0
        for x,y,trial in rows:
            a=weight if trial else 1.; margin=y*sum(p*q for p,q in zip(w,x))
            fac=-a*y/(1+math.exp(max(-30,min(30,margin))));mass+=a
            for j in range(3):g[j]+=fac*x[j]
        w=[a-.1*b/mass for a,b in zip(w,g)]
    return w

def metrics(w,rows):
    a={True:[],False:[]}
    for x,y,t in rows:
        pred=sum(p*q for p,q in zip(w,x)); a[t].append(1. if pred*y>0 else .5)
    return {'trial_MRR':round(sum(a[True])/len(a[True]),5),'reorder_MRR':round(sum(a[False])/len(a[False]),5)}

def smooth_target(target,size,epsilon=.2):return [(1-epsilon)*(i==target)+epsilon/size for i in range(size)]
def eligible_scores(logits,eligible):return {i:logits[i] for i in eligible}
def compute():
    train=samples(21,400); test=samples(22,400)
    out={str(r):metrics(fit(train,r),test) for r in [1,2,3,5]}
    assert abs(sum(smooth_target(1,4))-1)<1e-12
    assert 0 not in eligible_scores([99,2,1],[1,2])
    return {'note':'合成2候補のpairwise線形代理。比率の効果と配達可能集合の境界を確認。UVRの精度再現ではない。','verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},'experiments':[{'name':'trial重みを変え、未使用400セッションで再注文との交換条件を見る','seed':22,'metrics':out}], 'smoothed_target':smooth_target(1,4),'availability_example':eligible_scores([99,2,1],[1,2])}

if __name__ == "__main__":
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

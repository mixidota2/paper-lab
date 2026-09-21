"""Palette equations 9–14 and Algorithm 1 on a declared synthetic candidate pool.
No neural predictor is trained. Values and continuation probabilities are fixtures.
"""
import itertools, json, math
from pathlib import Path
ITEMS = [dict(id=i, value=v, group=g, duration=d, continuation=p)
         for i,(v,g,d,p) in enumerate([(10,0,40,.35),(9,0,20,.85),(8,1,30,.92),(7,1,10,.95),(6,2,15,.96),(5,2,25,.90),(4,3,20,.98)])]

def score(path, contextual=True, survival=True):
    value=0.; reach=1.; raw=[]
    for t,i in enumerate(path):
        item=ITEMS[i]
        fatigue=3*sum(ITEMS[j]['group']==item['group'] for j in path[:t]) if contextual else 0
        reward=item['value']-fatigue
        raw.append(reward); value+=reach*reward
        reach*=item['continuation'] if survival else 1
    return value,raw

def feasible(path):
    # Illustrative business rule, not a Meta policy.
    return len(set(path))==len(path) and all(not (a==0 and b==1) for a,b in zip(path,path[1:]))

def future(path, length, mode, raw):
    if not path or mode=='none':return 0.
    item=ITEMS[path[-1]]; exponent=1.
    if mode=='duration':exponent=sum(ITEMS[i]['duration'] for i in path)/len(path)/item['duration']
    return sum(raw)/len(raw)*sum(item['continuation']**(j*exponent) for j in range(1,length-len(path)+1))

def decode(beam=1, pool=7, contextual=True, survival=True, mode='none', budget=None, length=3):
    candidates=sorted(range(len(ITEMS)),key=lambda i:-ITEMS[i]['value'])[:pool]
    paths=[()]; calls=0; trace=[]
    for depth in range(length):
        expanded=[]
        for path in paths:
            for i in candidates:
                nxt=path+(i,)
                if not feasible(nxt):continue
                calls+=1
                if budget is not None and calls>budget:
                    result=decode(1,pool,False,False,'none',None,length)
                    return {**result,'fallback':True,'aborted_evaluations':calls}
                value,raw=score(nxt,contextual,survival)
                expanded.append((value+future(nxt,length,mode,raw),nxt))
        expanded.sort(key=lambda x:(-x[0],x[1]))
        paths=[p for _,p in expanded[:beam]]
        trace.append({'position':depth+1,'expanded':len(expanded),'kept':[list(p) for p in paths],'cutoff':expanded[min(beam,len(expanded))-1][0]})
    best=max(paths,key=lambda p:score(p,contextual,survival)[0])
    return {'path':list(best),'own_objective':round(score(best,contextual,survival)[0],6),'shared_survival_value':round(score(best)[0],6),'evaluations':calls,'fallback':False,'trace':trace}

def compute():
    runs={'pointwise':decode(contextual=False,survival=False),'CA_beam1':decode(survival=False),'golden_beam6':decode(6,mode='duration'),'trimmed_top3':decode(6,3,mode='duration'),'timeout':decode(6,mode='duration',budget=2)}
    oracle=max((p for p in itertools.permutations(range(7),3) if feasible(p)),key=lambda p:score(p)[0])
    assert runs['timeout']['path']==runs['pointwise']['path']
    return {'note':'合成7候補・3枠。学習済みCA、実測レイテンシー、本番liftは再現しない。','verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},'experiments':[{'name':'制約付き探索と候補切り詰め','metrics':{k:{'value':v['shared_survival_value'],'evaluations':v['evaluations']} for k,v in runs.items()}}],'runs':runs,'oracle':{'path':list(oracle),'value':score(oracle)[0]}}

if __name__ == "__main__":
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

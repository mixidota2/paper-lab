"""Synthetic exact-match SNIPS/LOO, not Netflix data or a ranker."""
import json,random
from pathlib import Path
P=[[.8,.1,.1],[.1,.2,.7]]
R=[[.6,.5,.1],[.1,.3,.2]]
FULL=[0,2]
LOO=[1,2]
def snips(log,policy,weight_scale=1):
    num=den=0.0
    for context,action,reward,propensity in log:
        if propensity<=0: raise ValueError('positive logging propensity required')
        if policy[context]==action:
            w=weight_scale/propensity
            num+=w*reward;den+=w
    if not den: raise ValueError('no support for target policy in log')
    return num/den
def exact(policy): return .4*R[0][policy[0]]+.6*R[1][policy[1]]
def simulate(n=120000,seed=23):
    rng=random.Random(seed);log=[]
    for _ in range(n):
        c=0 if rng.random()<.4 else 1
        a=rng.choices(range(3),weights=P[c])[0]
        log.append((c,a,int(rng.random()<R[c][a]),P[c][a]))
    full=snips(log,FULL);loo=snips(log,LOO)
    return dict(raw_log_mean=sum(x[2] for x in log)/n,snips_full=full,snips_loo=loo,incrementality=full-loo,true_full=exact(FULL),true_loo=exact(LOO),true_incrementality=exact(FULL)-exact(LOO),absolute_error=abs(full-loo-exact(FULL)+exact(LOO)))
def main():
    r=dict(note='人工データ。exact-match、1位置、既知propensity。NetflixのsimulationやA/Bの再現ではない。',verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'),experiments=[dict(name='同一探索ログでpolicyと除去policyを評価',n=120000,seed=23,metrics=simulate()),dict(name='cascade分解の算術例',metrics=dict(niche=.08*.2,broad=.03*.8))])
    Path(__file__).with_name('results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()

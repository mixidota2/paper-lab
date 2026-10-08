"""Unconditional exact McNemar power and transparent input-token accounting; stdlib only."""
import json, math, random
from functools import lru_cache
from pathlib import Path


def binom(n,p):
    if p==0: return [1.]+[0.]*n
    if p==1: return [0.]*n+[1.]
    return [math.exp(math.lgamma(n+1)-math.lgamma(k+1)-math.lgamma(n-k+1)+k*math.log(p)+(n-k)*math.log1p(-p)) for k in range(n+1)]


@lru_cache(None)
def rejection(m):
    null=binom(m,.5)
    tail=0
    accepted=[]
    for k in range(m+1):
        tail+=null[k]
        if k<=m/2 and 2*tail<=.05+1e-12: accepted.append(k)
    c=max(accepted,default=-1)
    return c


def power(n,q,gap):
    if not 0<=gap<=q: raise ValueError('gap must lie within discordance')
    out=0
    for m,pm in enumerate(binom(n,q)):
        c=rejection(m)
        if c<0 or pm<1e-15: continue
        alt=binom(m,(1+gap/q)/2)
        out+=pm*(sum(alt[:c+1])+sum(alt[m-c:]))
    return out


def mde(n,q,target):
    if power(n,q,q)<target: return None
    lo,hi=0,q
    for _ in range(24):
        mid=(lo+hi)/2
        if power(n,q,mid)>=target: hi=mid
        else: lo=mid
    return hi*100


def simulation(n,q,gap,reps=12000):
    rng=random.Random(20261008+n)
    rejected=0
    for _ in range(reps):
        b=c=0
        for _ in range(n):
            u=rng.random()
            b+=u<(q+gap)/2
            c+=(q+gap)/2<=u<q
        rejected+=min(b,c)<=rejection(b+c)
    return rejected/reps


def token_bill(preamble,slope,steps,ratio,hit=.97):
    inputs=steps*(preamble+554)+slope*steps*(steps-1)/2
    return {'input_tokens':inputs,'miss_price_equivalent_tokens':inputs*((1-hit)+hit*ratio)}


PAPER = {'source': 'Table 1 / Fig.2 / Appendix F–G, v1', 'flip': [13, 13, 22], 'pairs': [['3.6 CC−mini', -1.8, -5.2, 1.6], ['3.6 CC−OC', 2.9, -0.9, 6.7], ['3.6 mini−OC', 4.7, 1.1, 8.4], ['3.8 CC−mini', -1.4, -4.2, 1.5], ['3.8 CC−OC', 7.9, 4.3, 11.5], ['3.8 mini−OC', 9.2, 5.5, 12.9]]}


Q_HARD = 0.14008941877794337
Q_POOL = 0.14392803598200898


def main():
    check=[dict(n=n,q=q,gap_pp=g*100,exact_power=power(n,q,g),simulated_power=simulation(n,q,g)) for n,q,g in [(45,Q_HARD,.129),(447,Q_POOL,.052)]]
    assert all(abs(r['exact_power']-r['simulated_power'])<.02 for r in check)
    params={'Claude Code':[16581,937,88],'mini-SWE-agent':[829,648,80],'OpenCode':[7025,681,55]}
    bills={str(r):{k:token_bill(*v,r) for k,v in params.items()} for r in [.287,.033]}
    for bill in bills.values():
        assert bill['Claude Code']['input_tokens']>bill['mini-SWE-agent']['input_tokens']>bill['OpenCode']['input_tokens']
    grid=[]
    for n in [45,100,200,447,800]:
        for q in [.07,.14,.27,Q_HARD,Q_POOL]:
            grid.append(dict(n=n,q=q,mde50=mde(n,q,.5),mde80=mde(n,q,.8),ceiling=power(n,q,q)))
    result={'lab_kind':'harness08','note':'McNemar検出力は数理計算と乱数試行。token計算は入力のみの近似で、実API請求額の再現ではない。', 'checks':check,'power_grid':grid,'bill_params':params,'bills':bills,'experiments':[{'name':'検出力：不一致率14%','metrics':{'n45_mde50_pp':mde(45,.14,.5),'n45_mde80_pp':mde(45,.14,.8),'n45_ceiling':power(45,.14,.14),'n447_mde80_pp':mde(447,.14,.8)}}]}
    result['paper'] = PAPER
    result['official_resolution'] = {'q_hard':Q_HARD,'q_pool':Q_POOL,'n45_mde50_pp':mde(45,Q_HARD,.5),'n45_ceiling':power(45,Q_HARD,Q_HARD),'n447_mde80_pp':mde(447,Q_POOL,.8)}
    assert abs(result['official_resolution']['n45_mde50_pp']-12.89653749650708)<.002
    assert abs(result['official_resolution']['n447_mde80_pp']-5.159236787856072)<.002
    result['experiments'].append({'name':'著者コードの未丸め不一致率による照合','metrics':result['official_resolution']})
    (Path(__file__).parent/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(result['experiments'])

if __name__=='__main__': main()

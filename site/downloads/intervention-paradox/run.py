"""Paired-outcome accounting, threshold sweep and 50-task sampling uncertainty."""
import json
import random
from pathlib import Path


def accounting(a,b,c,d):
    n=a+b+c+d
    failures=a+c
    successes=b+d
    p=failures/n if n else None
    recovery=c/failures if failures else None
    disruption=b/successes if successes else None
    threshold=(disruption/(recovery+disruption) if recovery is not None and disruption is not None and recovery+disruption else None)
    return {'n':n,'p':p,'r':recovery,'d':disruption,'threshold':threshold,'delta':(c-b)/n if n else None}


def simulate_pilot(seed, p=.89, r=.12, d=.56, n=50):
    rng=random.Random(seed)
    counts=[0,0,0,0] # A,B,C,D
    for _ in range(n):
        failed=rng.random()<p
        changed=rng.random()<(r if failed else d)
        counts[(2 if changed else 0) if failed else (1 if changed else 3)]+=1
    return accounting(*counts)


def compute():
    pilots=[simulate_pilot(i) for i in range(2000)]
    rates=sorted(p['delta'] for p in pilots)
    frames=[{'p':p/100,'r':.12,'d':.56,'threshold':.56/.68,
             'recovered_per_100':p*.12,'disrupted_per_100':(100-p)*.56,
             'delta_pp':round(p*.12-(100-p)*.56,6)} for p in range(101)]
    exact=[]
    for a in range(6):
        for b in range(6):
            for c in range(6):
                for d in range(6):
                    x=accounting(a,b,c,d)
                    if x['r'] is not None and x['d'] is not None:
                        exact.append(abs(x['delta']-(x['p']*x['r']-(1-x['p'])*x['d'])))
    return {'note':'既知のBernoulli確率による合成pilot。論文の軌跡、AUROC、p値の再現ではない。',
            'experiments':[{'name':'50タスクpilotの判断のばらつき','dataset':'synthetic paired outcomes','n':2000,'seed':'0..1999',
                           'metrics':{'true_delta_pp':round(100*(.89*.12-(1-.89)*.56),6),'positive_observed_fraction':sum(p['delta']>0 for p in pilots)/len(pilots),
                                      'undefined_rate_fraction':sum(p['threshold'] is None for p in pilots)/len(pilots),
                                      'pilot_delta_pp_2.5_percentile':100*rates[49],'pilot_delta_pp_97.5_percentile':100*rates[1949],
                                      'max_accounting_error':max(exact)}}],
            'frames':frames,'example_pilot':simulate_pilot(16),
            'edge_cases':{'all_success':accounting(0,2,0,48),'all_failure':accounting(45,0,5,0),'no_change':accounting(25,0,0,25)}}


if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(compute(),ensure_ascii=False,indent=2)+'\n')

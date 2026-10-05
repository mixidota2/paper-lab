# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy==2.2.6", "scipy==1.18.1"]
# ///
"""Toy hurdle counts and exact threshold-AP normalization (paper Appendix B.1)."""
import itertools
import json
from pathlib import Path
import numpy as np
from scipy.stats import nbinom
from scipy.optimize import minimize
from scipy.special import expit


def metric(y, z):
    n, k = len(y), int(sum(y))
    if not 0 < k < n:
        return None
    order = np.argsort(-np.asarray(z), kind='stable')
    scores, labels = np.asarray(z)[order], np.asarray(y)[order]
    ends = np.r_[np.flatnonzero(scores[:-1] != scores[1:]) + 1, n]
    sizes = np.diff(np.r_[0, ends])
    cumulative = np.cumsum(labels)[ends - 1]
    positives = np.diff(np.r_[0, cumulative])
    ap = float(np.sum(positives * cumulative / ends) / k)
    ap0 = float((k - 1)/(n - 1) + (n-k)/(n*(n-1))*np.sum(sizes/ends))
    return {'ap': ap, 'ap0': ap0, 'skill': (ap-ap0)/(1-ap0)}


def validate():
    count, error = 0, 0.
    for n in range(2, 7):
        for cuts in itertools.product([0, 1], repeat=n-1):
            z = -np.cumsum([0, *cuts])
            for k in range(1, n):
                values=[]
                for chosen in itertools.combinations(range(n), k):
                    y=np.zeros(n); y[list(chosen)]=1
                    values.append(metric(y,z)['ap'])
                    count+=1
                error=max(error,abs(np.mean(values)-metric(y,z)['ap0']))
    assert error < 1e-12
    assert metric([1,0,0,1], [0]*4)['skill'] == 0
    pooled=metric([1,1,0,0,1,0,0,0], [1]*4+[0]*4)
    assert abs(pooled['skill']-1/15)<1e-12
    return {'enumerated_labelings': count, 'max_ap0_error': error, 'pooled_counterexample_skill': pooled['skill']}


def quantiles(p, mu):
    # Y = Bernoulli(p) * (1 + NB(r=2, mean=mu-1)); positive size is strictly positive.
    tau=np.arange(1,10)/10
    level=(tau-(1-p[...,None]))/p[...,None]
    q=np.where(level<=0, 0, 1+nbinom.ppf(np.clip(level,1e-12,1-1e-12),2,2/(mu[...,None]+1)))
    return q


def experiment(seed, varying):
    rng=np.random.default_rng(seed)
    x=rng.uniform(-2,2,(1000,64))
    p=1/(1+np.exp(2-0.9*x)) # all probabilities below 0.5
    mu=np.exp(1.5-1.2*x) if varying else np.full_like(x,5.)
    # Clip the conditional positive mean above one to preserve count support.
    mu=np.maximum(mu,1.01)
    y=(rng.random(p.shape)<p)*(1+rng.negative_binomial(2,2/(mu+1)))
    design=np.column_stack([np.ones(700*64),x[:700].ravel()])
    labels=(y[:700]>0).ravel()
    def loss(beta):
        logits=design@beta
        return np.mean(np.logaddexp(0,logits)-labels*logits), design.T@(expit(logits)-labels)/len(labels)
    fit=minimize(loss,np.zeros(2),jac=True,method='BFGS')
    assert fit.success
    beta=fit.x
    event=y[700:]>0
    q=quantiles(p[700:],mu[700:])
    methods={'中央値（真の分布）':q[:,:,4], '平均（真の分布）':p[700:]*mu[700:], '9分位点平均（真の分布）':q.mean(axis=-1), 'ロジスティック発生head':expit(beta[0]+beta[1]*x[700:])}
    rows=[]
    for name,z in methods.items():
        metrics=[metric(a,b) for a,b in zip(event,z)]
        valid=[m for m in metrics if m is not None]
        rows.append({'method':name,'ap_skill':float(np.mean([m['skill'] for m in valid])),'windows':len(valid)})
    return rows


def main():
    checks=validate()
    frames=[]
    for pct in range(1,100):
        p=pct/100; mu=np.array(5.); q=quantiles(np.array(p),mu)
        masses=[1-p]+[float(p*nbinom.pmf(k-1,2,1/3)) for k in range(1,21)]
        frames.append({'p':p,'median':float(q[4]),'mean':5*p,'quantile_average':float(q.mean()),'masses':masses})
    scenarios=[]
    for varying in [False,True]:
        runs=[experiment(seed,varying) for seed in [42,43,44]]
        rows=[]
        for i,r in enumerate(runs[0]):
            scores=[run[i]['ap_skill'] for run in runs]
            rows.append({**r,'ap_skill':float(np.mean(scores)),'seed_min':min(scores),'seed_max':max(scores)})
        scenarios.append({'varying_size':varying,'rows':rows})
    reported=[{'dataset':d,'reference':ref,'chronos2_point':point,'chronos2_probe':probe,'raw_lightgbm':tree} for d,ref,point,probe,tree in [('Amazon',.0078,.0057,.0130,.0091),('Favorita',.1026,.1160,.1932,.1957),('M5',.0434,.0453,.0762,.0642),('NYC taxi',.1853,.2117,.2237,.2243),('Web traffic',.0154,.0187,.0667,.1768)]]
    result={'lab05_sparse':True,'kind':'synthetic mechanism demonstration, not paper replication','seeds':[42,43,44],'horizon':64,'train_windows_per_seed':700,'test_windows_per_seed':300,'checks':checks,'distribution_frames':frames,'scenarios':scenarios,'reported':reported,'reported_source':'arXiv:2609.39386v1 Tables 14–18 (equal-window AP skill)','verification':{'mechanism':'CONFIRMED','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'checks':checks,'scenarios':scenarios},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()

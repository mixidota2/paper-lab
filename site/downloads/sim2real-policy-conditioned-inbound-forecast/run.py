# /// script
# dependencies = ["numpy==2.5.3"]
# ///
"""Policy-dependent inbound: shared exogenous tracks, misspecified simulator, causal calibration."""
import json
from pathlib import Path
import numpy as np


def rollout(seed, policy, scale=1.0, lead_bias=0, cost=None, weeks=260):
    rng = np.random.default_rng(seed)
    p = 24
    base = np.linspace(8, 28, p)
    demand = np.maximum(0, base * (1 + .3*np.sin(np.arange(weeks)[:,None]/6)) + rng.normal(0, 2, (weeks,p)))
    leads = rng.integers(1, 3, (weeks,p)) + lead_bias
    lam = np.repeat(rng.uniform(0, 5, (weeks+7)//8), 8)[:weeks] if cost is None else np.full(weeks,cost)
    inventory = base*3
    due = np.zeros((weeks+5,p))
    records = []
    for t in range(weeks):
        before = inventory.copy()
        inbound = due[t].copy()
        sales = np.minimum(demand[t],before+inbound)
        inventory = before+inbound-sales
        pipeline = due[t+1:].sum(axis=0)
        target = base * ((4.5 if policy=='new' else 2.8) - (.65 if policy=='new' else .12)*lam[t])
        steady = base*np.exp(-(.35 if policy=='new' else .02)*lam[t])
        order = scale*(.6*steady + .4*np.maximum(0,target-inventory-pipeline))
        for i in range(p):
            due[t+leads[t,i],i] += order[i]
        assert np.allclose(inventory,before+inbound-sales)
        # At origin t, next week's due orders (including today's orders) are still unknown to the forecaster.
        features = [1, np.sin(t/6), np.cos(t/6), float(lam[t]), inventory.sum()/p, pipeline.sum()/p, inbound.sum()/p]
        records.append(dict(t=t, x=features, inbound=float(inbound.sum()), demand=float(demand[t].sum()), inventory=float(inventory.sum()), orders=float(order.sum()), before=float(before.sum()), sales=float(sales.sum()), lam=float(lam[t])))
    x=np.array([r['x'] for r in records[12:-1]])
    y=np.array([r['inbound'] for r in records[13:]])
    return x,y,records


def fit(x,y):
    return np.linalg.lstsq(x,y,rcond=None)[0]


def mape(y,p):
    return float(np.mean(np.abs(y-p)/np.maximum(y,1))*100)


def calibrate(prediction, truth):
    calibrated=[]
    for t in range(4,len(truth)):
        ab=fit(np.column_stack([np.ones(t),prediction[:t]]),truth[:t])
        calibrated.append(float(ab[0]+ab[1]*prediction[t]))
    return np.array(calibrated)


def experiment(seed):
    train=[]
    for s in range(seed,seed+12):
        train.append((rollout(s,'old'),rollout(s,'new',scale=.7,lead_bias=1)))
    hist=fit(np.concatenate([a[0] for a,b in train]),np.concatenate([a[1] for a,b in train]))
    sim=fit(np.concatenate([b[0] for a,b in train]),np.concatenate([b[1] for a,b in train]))
    x,y,_=rollout(seed+1000,'new')
    ph,ps=x@hist,x@sim
    calibrated=calibrate(ps,y)
    calibrated_hist=calibrate(ph,y)
    return {'seed':seed,'history_mape':mape(y[4:],ph[4:]),'sim_mape':mape(y[4:],ps[4:]),'calibrated_mape':mape(y[4:],calibrated), 'calibrated_history_mape':mape(y[4:],calibrated_hist), 'n_test':len(y)-4}



PAPER = {'source': 'Table 2–3, v1', 'horizons': ['1週', '2週', '3週', '4〜10週'], 'studies': {'S1': {'sim': [13.3, 11.7, 13.2, 14.8], 'sim_ci': [2.7, 2.8, 3.1, 2.8], 'history': [15, 14.8, 15.2, 16], 'history_ci': [2.9, 3.1, 3.1, 3.1], 'cal': [11.8, 11.2, 13.1, 14.8]}, 'S2': {'sim': [12.7, 15.3, 9.4, 11.5], 'sim_ci': [3.6, 7.4, 3.8, 3.4], 'history': [25.6, 27.8, 28.1, 25.2], 'history_ci': [5.2, 6.3, 6.4, 5.7], 'cal': [12.6, 13, 6.9, 9.7]}}, 'fidelity': [['発注', 0.705, 0.24], ['入荷', 0.67, 0.47], ['在庫', 0.905, 0.81], ['販売', 0.995, 0.92]]}


def main():
    trials=[experiment(s) for s in [7,19,43,71,101]]
    traces={str(c):rollout(7,'new',cost=c,weeks=40)[2][:24] for c in [0,2,4]}
    assert all(traces['0'][t]['demand']==traces['4'][t]['demand'] for t in range(24))
    result={'lab_kind':'sim08','seed':7,'note':'人工的な24商品の実験。CNN、Amazonのデータ、原論文の性能は再現していない。MAPEは同じ新方策の期間で比較する。', 'trials':trials,'traces':traces,
      'experiments':[{'name':'新方策への移行：5 seed平均','metrics':{k:round(float(np.mean([r[k] for r in trials])),3) for k in ['history_mape','sim_mape','calibrated_mape','calibrated_history_mape']}}]}
    result['paper'] = PAPER
    (Path(__file__).parent/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(result['experiments'])

if __name__=='__main__': main()

"""Exact finite-population DR and replay check, with enumerated randomization."""
import json
from pathlib import Path

# Each type has 100 outcomes per arm, exactly enumerating e=.5.
# The nuisance outcome model is deliberately wrong in both arms.
TYPES = [('low',.10,.08),('medium',.40,.20),('organic',.80,.75)]
rows=[]
for name,p1,p0 in TYPES:
    for treatment,p in [(0,p0),(1,p1)]:
        for i in range(100):
            rows.append(dict(name=name,score=p1,t=treatment,y=int(i<round(p*100)),p1=p1,p0=p0))

def dr(row,e=.5):
    mu1,mu0=.3,.2
    t,y=row['t'],row['y']
    return mu1-mu0+t*(y-mu1)/e-(1-t)*(y-mu0)/(1-e)

def evaluate(threshold):
    matched=[r for r in rows if int(r['score']>threshold)==r['t']]
    replay=sum(r['y'] for r in matched)/len(matched)
    truth=sum(p1 if p1>threshold else p0 for _,p1,p0 in TYPES)/len(TYPES)
    assert abs(replay-truth)<1e-12
    return {'threshold':threshold,'trigger_rate':sum(p1>threshold for _,p1,_ in TYPES)/3,
            'replay_reward':round(replay,6),'true_reward':round(truth,6)}

estimates=[]
for name,p1,p0 in TYPES:
    group=[r for r in rows if r['name']==name]
    estimate=sum(dr(r) for r in group)/len(group)
    wrong=sum(dr(r,.8) for r in group)/len(group)
    assert abs(estimate-(p1-p0))<1e-12
    estimates.append({'type':name,'true_uplift':round(p1-p0,6),'dr_known_propensity':round(estimate,6),'dr_wrong_propensity':round(wrong,6)})
sweep=[evaluate(t) for t in [0,.1,.3,.4,.7,.8,1]]
out={'experiment':'enumerated_randomized_holdout','n':len(rows),'verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},'dr':estimates,'sweep':sweep,'checks':{'untruncated_dr_with_wrong_outcomes':True,'balanced_replay_equals_policy_truth':True,'wrong_propensity_bias_observed':any(abs(x['dr_wrong_propensity']-x['true_uplift'])>.01 for x in estimates)},'explorer':{'label':'SV の発火閾値 δ','unit':'%','metric':'合成 Holdout の発火率と報酬率','default':2,'frames':[{'value':x['threshold'],'note':'合成データの厳密平均。論文の A/B や学習済みモデルの再現ではない。','bars':[{'label':'CG 発火率','value':round(100*x['trigger_rate'],3)},{'label':'replay 報酬率','value':100*x['replay_reward']},{'label':'真の方策報酬率','value':100*x['true_reward']}]} for x in sweep]}}
Path(__file__).with_name('results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out['checks']))

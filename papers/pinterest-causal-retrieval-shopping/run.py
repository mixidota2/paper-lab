"""割付と結果を先に決めた人工例で、補正式と、記録を使ったしきい値の試算を確かめる。"""
import json
from pathlib import Path

# リクエストの種類ごとに、呼ぶ群と呼ばない群を各100件用意する。割付確率は0.5。
# 両方の群で、結果の予測値は実際に起きる割合と異なる値にする。
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
out={'experiment':'enumerated_randomized_holdout','n':len(rows),'verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},'dr':estimates,'sweep':sweep,'checks':{'untruncated_dr_with_wrong_outcomes':True,'balanced_replay_equals_policy_truth':True,'wrong_propensity_bias_observed':any(abs(x['dr_wrong_propensity']-x['true_uplift'])>.01 for x in estimates)},'explorer':{'label':'候補を探すか決めるしきい値 δ','unit':'%','metric':'人工例での呼び出し率と反応が起きた割合','default':2,'frames':[{'value':x['threshold'],'note':'候補を探すかどうかが、しきい値の判断と一致した記録だけを使った。論文の本番試験や学習済みモデルは再現していない。','bars':[{'label':'候補を探す割合','value':round(100*x['trigger_rate'],3)},{'label':'記録から求めた反応率','value':100*x['replay_reward']},{'label':'設定した確率から求めた反応率','value':100*x['true_reward']}]} for x in sweep]}}
Path(__file__).with_name('results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out['checks']))

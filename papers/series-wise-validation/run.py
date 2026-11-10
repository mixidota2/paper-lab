"""Independent explanatory experiment; no author implementation is executed."""
from pathlib import Path
import json
import math
from collections import Counter

ROOT = Path(__file__).parent
IDS = 'ABCDEFGHIJ'
P, H = 8, 4
INPUT_LIMIT = 1_000_000
# evaluate is the validated public entry. Other helpers serve this fixed toy and tests.


def dataset():
    return {s: [10 + 2*i + (.1 if i < 5 else .4 if i < 7 else .7)*t
                + .4*((t+i) % 4) for t in range(1, 101)] for i,s in enumerate(IDS)}


def origins(cutoff):
    if not isinstance(cutoff,int) or not P+H <= cutoff <= 92:
        raise ValueError('training cutoff must be an integer in 12..92')
    return list(range(P, cutoff-H+1))


def fit(data, ids, cutoff):
    # Every training target ends by cutoff; origins <= cutoff is insufficient.
    samples = [(data[s][o+H-1]-data[s][o-1])/H for s in ids for o in origins(cutoff)]
    return sum(samples)/len(samples)


def predict(data, s, origin, family, scale, slope):
    if len(s)!=1 or s not in IDS or not isinstance(origin,int) or not P <= origin <= 96:
        raise ValueError('invalid series or origin')
    if family not in ('global','context') or scale not in (0,1):
        raise ValueError('invalid toy candidate')
    context=data[s][origin-P:origin]
    local=(context[-1]-context[0])/(P-1)
    trend=slope if family=='global' else local
    return [context[-1]+scale*trend*j for j in range(1,H+1)]


def score(data, ids, origin, family, scale, slope):
    errors=[abs(a-b) for s in ids for a,b in zip(
        data[s][origin:origin+H],predict(data,s,origin,family,scale,slope))]
    return sum(errors)/len(errors)


def select(data, scheme='series'):
    if scheme not in ('series','time'): raise ValueError('unknown split')
    inner_slope=fit(data,IDS[:5],84)
    outer_slope=fit(data,IDS[:5],88)
    validation=IDS[5:7] if scheme=='series' else IDS[:5]
    candidates=[]
    for family in ('global','context'):
        inner=[score(data,IDS[:5],84,family,k,inner_slope) for k in (0,1)]
        scale=min((0,1),key=lambda k:(inner[k],k))
        candidates.append({'family':family,'scale':scale,'inner_mae':inner[scale],
                           'outer_mae':score(data,validation,88,family,scale,outer_slope)})
    chosen=min(candidates,key=lambda c:(c['outer_mae'],c['family']!='global'))
    return {'scheme':scheme,'candidates':candidates,'chosen':chosen.copy(),
            'inner_last_origin':origins(84)[-1],'outer_last_origin':origins(88)[-1],
            'final_last_origin':origins(92)[-1],'outer_validation_ids':validation}


def scale_q(data):
    errors=[abs(data[s][t]-data[s][t-4]) for s in IDS[:7] for t in range(4,92)]
    return sum(errors)/len(errors)


def evaluate(data=None,scheme='series',q=None):
    data=dataset() if data is None else data
    if (not isinstance(data,dict) or set(data)!=set(IDS) or
        any(type(data[s]) is not list or len(data[s])!=100 or
            any(type(x) not in (int,float) or not -INPUT_LIMIT <= x <= INPUT_LIMIT
                or not math.isfinite(x) for x in data[s]) for s in IDS)):
        raise ValueError('ten dense 100-point lists of finite numbers in -1000000..1000000 required')
    selection=select(data,scheme);chosen=selection['chosen'];slope=fit(data,IDS[:7],92)
    q=scale_q(data) if q is None else q
    if type(q) not in (int,float) or not 0<=q<=INPUT_LIMIT or not math.isfinite(q):
        raise ValueError('Q must be a finite number in 0..1000000')
    records=[]
    for s in IDS:
        for origin in range(92,97):
            pred=predict(data,s,origin,chosen['family'],chosen['scale'],slope)
            records.append({'series':s,'origin':origin,'context_times':list(range(origin-7,origin+1)),
                'target_times':list(range(origin+1,origin+5)),'prediction':pred,
                'actual':data[s][origin:origin+4],
                'errors':[abs(a-b) for a,b in zip(data[s][origin:origin+4],pred)]})
    mae=sum(sum(r['errors']) for r in records)/(len(records)*H)
    weights=dict(sorted(Counter(t for r in records if r['series']=='A' for t in r['target_times']).items()))
    by_time=[sum(r['errors'][r['target_times'].index(t)] for r in records if r['series']==s and t in r['target_times'])/weights[t] for s in IDS for t in range(93,101)]
    mase=None if q==0 else mae/q
    equal=sum(by_time)/len(by_time)
    if any(not math.isfinite(x) for x in (mae,equal,slope,q)) or (mase is not None and not math.isfinite(mase)):
        raise ValueError('nonfinite result; positive Q may be too small')
    return {'synthetic':True,'model_version':'series-cv-toy-1','selection':selection,
        'fixed_final_slope':slope,'Q':q,'MAE':mae,'MASE':mase,
        'equal_target_time_MAE':equal,'weights':weights,'records':records}


def sensitivity(method='Holdout',include_weather=True):
    table=json.loads((ROOT/'table3.json').read_text())
    j=table['methods'].index(method);rows=table['rows']
    active={k:v for k,v in rows.items() if include_weather or k!='Weather'}
    delta={k:v[-1]-v[j] for k,v in active.items()}
    base=sum(v[-1] for v in active.values())
    total=sum(delta.values());weather=delta.get('Weather',0)
    return {'method':method,'dataset_count':len(active),'displayed_row_mean':sum(v[j] for v in active.values())/len(active),
        'published_full_mean':table['published_mean'][j], 'wins_vs_time':sum(x>1e-12 for x in delta.values()),
        'ties_vs_time':sum(abs(x)<=1e-12 for x in delta.values()),'delta_sum':total,
        'mean_difference_ratio':total/base,'weather_contribution':None if not total else weather/total,
        'per_dataset_delta':delta}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results.json');a=p.parse_args()
    a.out.write_text(json.dumps({'toy':evaluate(),'table3_checks':{m:sensitivity(m) for m in ('Holdout','K-MC-CV','Kf-CV')},'without_weather':{m:sensitivity(m,False) for m in ('Holdout','K-MC-CV','Kf-CV')}},ensure_ascii=False,indent=2,allow_nan=False)+'\n')

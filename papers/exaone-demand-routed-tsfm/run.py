"""Small mechanism experiment; no EXAONE weights or learned neural router."""
import json
import math
import random
from pathlib import Path
from statistics import mean, pvariance

CLASSES = ['Smooth', 'Intermittent', 'Erratic', 'Lumpy']

def membership(adi, cv2, temperature=1):
    a = 1 / (1 + math.exp(-(math.log(adi)-math.log(1.32))/.35))
    c = 1 / (1 + math.exp(-(math.log(max(cv2, 1e-12))-math.log(.49))/.60))
    p = [(1-a)*(1-c), a*(1-c), (1-a)*c, a*c]
    p = [v**(1/temperature) for v in p]
    return [v/sum(p) for v in p]

def stats(x):
    eps = .001*mean(abs(v) for v in x)
    z = [abs(v) for v in x if abs(v)>eps]
    return len(x)/max(len(z),1), pvariance(z)/mean(z)**2 if z else 0

def forecasts(x, alpha=.15):
    ses=x[0]; size=next((v for v in x if v>0),0); interval=1.; gap=1
    prob=sum(v>0 for v in x[:10])/10
    ts_size=size
    for v in x[1:]:
        ses += alpha*(v-ses)
        prob += alpha*((v>0)-prob)
        if v>0:
            size += alpha*(v-size)
            interval += alpha*(gap-interval)
            ts_size += alpha*(v-ts_size)
            gap=1
        else:
            gap+=1
    croston=size/interval
    return [ses,croston,(1-alpha/2)*croston,prob*ts_size]

def generate(rng, kind, n=180):
    p=[.96,.25,.96,.25][kind]
    shape=[15,15,.6,.6][kind]
    return [max(1,round(rng.gammavariate(shape,8/shape))) if rng.random()<p else 0 for _ in range(n)]

def main():
    rows=[]; by_seed=[]
    # Same histories / horizons; global method selected on separate validation series.
    for seed in [7,19,41,73,101]:
        rng=random.Random(seed)
        validation=[generate(rng,k) for k in range(4) for _ in range(40)]
        losses=[mean(mean(abs(y-f) for y in x[150:]) for x in validation for f in [forecasts(x[:150])[j]]) for j in range(4)]
        selected=min(range(4), key=lambda j:losses[j])
        seed_rows=[]
        for k in range(4):
            pairs=[]
            for _ in range(80):
                x=generate(rng,k); train=x[:150]; target=x[150:]
                fs=forecasts(train); p=membership(*stats(train))
                # Class-to-method assignment is an explanatory assumption, not learned EXAONE routing.
                routed=sum(w*f for w,f in zip(p,[fs[0],fs[2],fs[1],fs[3]]))
                scale=mean(abs(a-b) for a,b in zip(train,train[1:]))
                pairs.append([mean(abs(y-f) for y in target)/scale for f in [fs[selected],routed]])
            seed_rows.append([mean(v[j] for v in pairs) for j in range(2)])
        by_seed.append({'seed':seed,'global_method':['SES','Croston','SBA','TSB'][selected], 'mase_global':mean(r[0] for r in seed_rows),'mase_routed':mean(r[1] for r in seed_rows)})
        rows.append(seed_rows)
    checks={'membership_sums_to_one':all(abs(sum(membership(a,c))-1)<1e-12 for a in [1,1.32,3,20] for c in [0,.49,2]),'boundary_is_uniform':all(abs(p-.25)<1e-12 for p in membership(1.32,.49)), 'scale_invariance': all(abs(a-b)<1e-10 for a,b in zip(stats([0,2,4,0,3]),stats([0,20,40,0,30])))}
    assert all(checks.values())
    result={'lab05_exaone':True,'scope':'人工データで分類比率と古典予測器の混合を確認。EXAONEの再現ではない。','seed_results':by_seed,'class_results':[{'class':c,'global':mean(r[k][0] for r in rows),'routed':mean(r[k][1] for r in rows)} for k,c in enumerate(CLASSES)],'checks':checks,'verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},'reported_aggregate':[['EXAONE Demand',1.0667],['Synthetic',1.0742],['TiRex-1.1',1.0818],['Chronos-2',1.0885],['Backbone',1.1050]],'reported_datasets':DATASETS}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(by_seed,indent=2))

# Table 9: EXAONE, synthetic-only, TiRex-1.1, Chronos-2 (reported, not reproduced).
DATASETS=[['Bitbrains fast (H)',1.020,1.008,1.016,.995],['Bitbrains random (H)',5.829,5.832,5.859,5.853],['BizITObs L2C (H)',.441,.445,.487,.439],['Car parts (M)',.828,.847,.916,.900],['Electricity (D)',1.375,1.383,1.466,1.415],['Electricity (H)',1.010,1.009,.912,.888],['Electricity (W)',1.494,1.468,1.478,1.456],['Hierarchical sales (D)',.746,.761,.768,.768],['Hierarchical sales (W)',.719,.722,.747,.745],['Hospital (M)',.759,.765,.785,.807],['Loop Seattle (D)',.889,.891,.900,.928],['Loop Seattle (H)',.817,.819,.820,.816],['M4 daily (D)',3.079,3.046,3.063,3.164],['M4 hourly (H)',.763,.805,.708,.800],['M4 monthly (M)',.909,.925,.938,.943],['M4 quarterly (Q)',1.149,1.150,1.118,1.177],['M4 weekly (W)',2.066,2.150,1.973,2.070],['M4 yearly (Y)',3.165,3.217,3.238,3.256],['M-dense (D)',.645,.640,.678,.681],['M-dense (H)',.786,.783,.802,.807],['Restaurant (D)',.676,.677,.704,.713],['SZ taxi (H)',.566,.567,.582,.591]]
if __name__=='__main__':main()

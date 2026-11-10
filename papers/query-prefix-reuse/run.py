"""Self-authored finite SID toy. Public scalar API: toy(), projection(), checks().
No trained model, timing measurement, arbitrary vector API, or log replay.
"""
import json
import math
from pathlib import Path

VERSION = 'query-prefix-reuse-toy-1'
TABLE1 = [dict(method='0.5B E2E', hr=81.99, recall=45.53, ms=117),
          dict(method='7B E2E', hr=85.71, recall=50.96, ms=168.88),
          dict(method='ReuseGR prepared', hr=85.82, recall=46.05, ms=71.45)]
PRESETS = [dict(name=n, q=q, p=p, hr=h, ms=t, quality=k) for n,q,p,h,t,k in [
    ('Prepared',100,100,85.82,71.45,'endpoint'), ('Cold',0,0,81.99,117,'endpoint'),
    ('Static Q',20.97,36.87,82.38,100.21,'measured partition'),
    ('Static mix',20.97,36.87,83.40,100.21,'projection'),
    ('Backfill',42.15,58.40,84.23,90.40,'projection'),
    ('Rolling 1M',68.50,84.20,85.21,78.65,'projection')]]


def _integer(x, low, high):
    if type(x) not in (int,float) or not math.isfinite(x) or int(x)!=x or not low<=x<=high:
        raise ValueError('integer outside domain')
    return int(x)


def projection(p):
    if type(p) not in (int,float) or not math.isfinite(p) or not 0<=p<=1:
        raise ValueError('finite numeric P in [0, 1] required')
    return dict(p=p, mean_ms=p*71.45+(1-p)*117,
                hr_percent=p*85.82+(1-p)*81.99, recall_percent=p*46.05+(1-p)*45.53,
                kind='fixed-endpoint projection; not measured mixed traffic')


def toy(prepared=True, depth=1, query='wide', history='left', budget=4):
    if type(prepared) is not bool:
        raise ValueError('prepared must be boolean')
    depth,budget=_integer(depth,0,3),_integer(budget,0,8)
    if query not in ('wide','narrow') or history not in ('left','right'):
        raise ValueError('unknown query or history')
    # Authored prefix sets, NOT CellPlan outputs or empirical frequency lookup.
    sets={'wide':[[''],['0','1'],['00','10'],['000','100']],
          'narrow':[[''],['0'],['00'],['000']]}
    active_depth=depth if prepared else 0
    prefixes=sets[query][active_depth]
    target='0001' if history=='left' else '1111'
    reachable=[format(i,'04b') for i in range(16)
               if any(format(i,'04b').startswith(c) for c in prefixes)]
    def score(s):
        return sum(s[j]=='0' for j in range(active_depth))+sum(
            (j+1)*int(s[j]==target[j]) for j in range(active_depth,4))
    ranked=sorted(reachable,key=lambda s:(-score(s),s))
    branches=sorted({s[:3] for s in reachable},key=lambda b:(
        -max(score(s) for s in reachable if s.startswith(b)),b))
    # Artificial admission knob, including d=3. Cold bypasses admission.
    admitted=branches[:budget] if prepared else branches
    final=[s for s in ranked if s[:3] in admitted]
    return dict(synthetic=True,model_version=VERSION,
        input=dict(prepared=prepared,depth=depth,query=query,history=history,budget=budget),
        route=('prepared-root' if depth==0 else 'prepared-prefix') if prepared else 'cold-e2e',
        waits_for_planner=False,async_prepare=(not prepared and depth>0),
        active_depth=active_depth,prefixes=prefixes,target=target,reachable=reachable,
        target_reachable=target in reachable,
        layer_nodes=[len({s[:j] for s in reachable}) for j in range(1,5)],
        l4_scored=len(reachable),branches=branches,admitted=admitted,
        ranking=[dict(sid=s,score=score(s)) for s in final],target_returned=target in final)


def checks():
    saving=117-71.45
    return dict(model_version=VERSION,synthetic=True,
        source='https://arxiv.org/html/2611.04259v1',published_table1=TABLE1,published_table5=PRESETS,
        projections=[projection(v['p']/100) for v in PRESETS],
        prepared_stages_ms=sum([.18,67.01,3.84,.42]),planning_ms=88,saving_ms=saving,
        compute_hits=math.ceil(88/saving),refresh_gpu_hours=1_000_000*.1*88/3_600_000,
        positive_depth_within_prepared_percent=36779/44225*100,
        default=toy(),deep_counterexample=toy(True,3,'wide','right',8),
        root_comparison=toy(True,0,'wide','right',8),cold_comparison=toy(False,3,'wide','right',8),
        not_tested=['models','commercial logs','money','queue','P95 mixture','P99','online lift'])


if __name__=='__main__':
    Path(__file__).with_name('results.json').write_text(
        json.dumps(checks(),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

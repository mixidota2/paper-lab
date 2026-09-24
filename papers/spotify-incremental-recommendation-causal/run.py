"""Synthetic policy check; no Spotify data, model fitting or causal estimation."""
import json
from pathlib import Path

# Scores deliberately refer to different windows. True same-window outcomes
# are supplied separately only so this synthetic policy can be evaluated.
ROWS = [
    {'name': 'organic', 'p1_short': .70, 'p0_long': .90, 'y1': .92, 'y0': .90},
    {'name': 'persuadable', 'p1_short': .60, 'p0_long': .15, 'y1': .75, 'y0': .15},
    {'name': 'low_response', 'p1_short': .10, 'p0_long': .05, 'y1': .15, 'y0': .05},
    {'name': 'mixed', 'p1_short': .50, 'p0_long': .45, 'y1': .65, 'y0': .45},
]

def evaluate(theta0):
    chosen = [r for r in ROWS if r['p1_short'] >= .4 and r['p0_long'] <= theta0]
    return {'theta0': theta0, 'selected': [r['name'] for r in chosen],
            'impressions': len(chosen),
            'expected_incremental_streams': round(sum(r['y1']-r['y0'] for r in chosen), 4),
            'expected_total_streams': round(sum(r['y1'] if r in chosen else r['y0'] for r in ROWS), 4)}

sweep = [evaluate(t/10) for t in range(11)]
assert all(a['impressions'] <= b['impressions'] for a,b in zip(sweep,sweep[1:]))
assert sweep[-1]['impressions'] == 3
assert evaluate(.2)['selected'] == ['persuadable']
assert ROWS[0]['p1_short']-ROWS[0]['p0_long'] < 0 < ROWS[0]['y1']-ROWS[0]['y0']
out = {'experiment': 'synthetic_dual_threshold', 'verification': {'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},
       'rows': ROWS, 'baseline':evaluate(1), 'proposed':evaluate(.5), 'sweep':sweep,
       'checks':{'theta0_monotonicity':True,'baseline_at_one':True,'mismatched_subtraction_sign_counterexample':True},
       'explorer':{'label':'自然再生の上限 θ₀','unit':'件','metric':'4組の合成データで表示する件数','default':5,'frames':[
           {'value':x['theta0'],'note':f"合成例。追加再生の期待値 {x['expected_incremental_streams']}、全再生の期待値 {x['expected_total_streams']}。実測値ではない。",'bars':[{'label':'単一閾値','value':3},{'label':'二重閾値','value':x['impressions']}]} for x in sweep]}}
Path(__file__).with_name('results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out['checks']))

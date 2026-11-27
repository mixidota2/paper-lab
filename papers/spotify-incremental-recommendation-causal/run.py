"""架空の組で表示条件を計算する。Spotifyのデータや学習済みモデルは使わない。"""
import json
from pathlib import Path

# 二つの予測値は異なる期間で測る。同じ期間での再生確率は、教材の比較用に別に置く。
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
       'explorer':{'label':'推薦なしで再生する確率をどこまで許すか（θ₀）','unit':'（確率）','metric':'仮の4組のうち推薦を表示する件数','default':5,'frames':[
           {'value':x['theta0'],'note':f"4組を合計した期待値は、推薦で増える再生が {x['expected_incremental_streams']}、全再生が {x['expected_total_streams']}です。いずれも仮の数値から計算しました。",'bars':[{'label':'表示後の確率だけで選ぶ','value':3},{'label':'自然再生の確率も使って選ぶ','value':x['impressions']}]} for x in sweep]}}
Path(__file__).with_name('results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out['checks']))

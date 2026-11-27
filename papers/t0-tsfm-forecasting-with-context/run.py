"""報告値の差と人工例の情報の流れ・分位点を計算する。t0は実行しない。"""
import json,math
from pathlib import Path
def skill_audit(off,on):
    return dict(without=off,with_covariates=on,lift_pp=round(on-off,6),implied_geomean_loss_relative_change=(1-on/100)/(1-off/100)-1)
def propagate(allow_future_to_read_target=False):
    # Two patch positions; edges mean a query output reads an input.
    nodes=[('y',0),('y',1),('z',0),('z',1)]
    state={n:{n} for n in nodes}
    def variate(s):
        return {n:set().union(*(s[k] for k in nodes if k[1]==n[1] and (n[0]=='y' or k[0]=='z' or allow_future_to_read_target))) for n in nodes}
    def time(s):
        return {n:set().union(*(s[k] for k in nodes if k[0]==n[0] and (n[0]=='z' or k[1]<=n[1]))) for n in nodes}
    final=variate(time(variate(state)))
    return ('y',1) in final[('y',0)]
def ordered_quantiles(base,raw):
    values=[base]
    for r in raw:values.append(values[-1]+max(r,0)+math.log1p(math.exp(-abs(r))))
    return values
def main():
    r=dict(note='Labは表5の丸め済みの値から差を求め、人工例で情報の伝わり方と分位点の順序を確認する。t0の重みは使わない。',verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'),author_value_audit=dict(known_future=skill_audit(36.7,43),past_only=skill_audit(32.9,35.6)),future_target_leak=dict(symmetric=propagate(True),asymmetric=propagate(False)),quantile_toy=ordered_quantiles(-1,[-2,0,1,2]))
    Path(__file__).with_name('results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()

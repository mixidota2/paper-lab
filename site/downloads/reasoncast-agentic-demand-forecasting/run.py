"""Standalone deterministic teaching experiment; standard library only."""
import math

def correct(base, route, additive, level, gate=1.0):
    # An explicit bypass preserves even the floating-point bit pattern.
    if route == 'Skip':
        return list(base)
    if route not in ('Basic', 'Tool'):
        raise ValueError(route)
    return [(b + gate*a)*math.exp(gate*r) for b,a,r in zip(base,additive,level)]

def wmape(actual, prediction):
    denominator=sum(abs(y) for y in actual)
    if not denominator: return None
    return 100*sum(abs(y-p) for y,p in zip(actual,prediction))/denominator

def experiment():
    frames=[]
    for name,actual,route,a,r in [
        ('平常期・Skip', [10,10,10], 'Skip', [0,0,0], [math.log(1.2)]*3),
        ('平常期・不要なBasic', [10,10,10], 'Basic', [0,0,0], [math.log(1.2)]*3),
        ('イベント・Basic', [10,20,10], 'Basic', [0,10,0], [0,0,0]),
        ('水準変化・Tool', [20,20,20], 'Tool', [0,0,0], [math.log(2)]*3),
        ('誤った意味情報・Tool', [10,10,10], 'Tool', [0,0,0], [math.log(2)]*3)]:
        base=[10,10,10]; pred=correct(base,route,a,r)
        frames.append(dict(label=name,route=route,actual=actual,base=base,prediction=pred,baseline_wmape=wmape(actual,base),proposed_wmape=wmape(actual,pred)))
    return dict(lab28='reasoncast',frames=frames,checks={'skip_exact': correct([0.1,-0.0,1e100],'Skip',[float('nan')]*3,[float('inf')]*3)==[0.1,-0.0,1e100]})

if __name__ == '__main__':
    import json
    from pathlib import Path
    result=experiment()
    result['note']='教育用の人工例。原論文の学習・性能・本番効果は再現していない。'
    result['verification']={'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))

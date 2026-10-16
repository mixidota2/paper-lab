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

def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def evaluate(inputs):
    """Seven-day output-space proxy; observed y never determines routing/prediction."""
    for key in ('base', 'actual', 'additive', 'level'):
        if not isinstance(inputs.get(key), list) or len(inputs[key]) != 7 or not all(finite(x) for x in inputs[key]):
            raise ValueError(key + ': finite 7-day array required')
    if any(y < 0 for y in inputs['actual']):
        raise ValueError('actual must be nonnegative')
    g = inputs.get('gate')
    if not finite(g) or not 0 <= g <= 1 or inputs.get('route') not in ('Skip', 'Correct'):
        raise ValueError('invalid gate or route')
    b, y, a, level = (inputs[k] for k in ('base', 'actual', 'additive', 'level'))
    try:
        always = correct(b, 'Basic', a, level, 1)
        selected = correct(b, 'Skip' if inputs['route'] == 'Skip' else 'Basic', a, level, g)
    except OverflowError as error:
        raise ValueError('correction overflow') from error
    if not all(finite(v) for v in always + selected):
        raise ValueError('nonfinite prediction')
    rows = []
    denominator = sum(y)
    for name, prediction in [('baseline', list(b)), ('always', always), ('selected', selected)]:
        errors = [abs(v-p) for v,p in zip(y,prediction)]
        total = sum(errors)
        if not finite(total) or not finite(denominator):
            raise ValueError('metric overflow')
        rows.append(dict(name=name, prediction=prediction, errors=errors, error_sum=total,
                         denominator=denominator, mae=total/7, wmape=None if denominator == 0 else 100*(total/denominator)))
    baseline = rows[0]['wmape']
    for row in rows:
        row['delta_pp'] = None if baseline is None else row['wmape'] - baseline
    return dict(rows=rows, route=inputs['route'], negative_prediction=any(v < 0 for v in always+selected))


def reference_cases():
    default = dict(base=[10]*7, actual=[20]*7, additive=[0]*7, level=[math.log(2)]*7, gate=.5, route='Correct')
    return dict(inputs=default, output=evaluate(default))


if __name__ == '__main__':
    import argparse, json
    from pathlib import Path
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path)
    args = parser.parse_args()
    if args.input:
        payload = json.loads(args.input.read_text())
        print(json.dumps(evaluate(payload['inputs']), ensure_ascii=False, allow_nan=False, indent=2))
        raise SystemExit(0)

    import json
    from pathlib import Path
    result=experiment()
    result['reference'] = reference_cases()
    result['note']='教育用の人工例。原論文の学習・性能・本番効果は再現していない。'
    result['verification']={'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))

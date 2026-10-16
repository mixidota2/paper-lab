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

MODEL_SPEC = {'id': 'reasoncast-output-proxy', 'version': '2.0.0', 'source': {'url': 'https://arxiv.org/html/2608.15291v1', 'version': 'arXiv:2608.15291v1'}, 'conventions': {'prediction': 'Seven-day output-space proxy (b+g*a)*exp(g*l), not paper Eq.8; Skip copies base without correction.', 'metrics': 'WMAPE percent=100*sum(abs(y-p))/sum(y); zero denominator is null; MAE in original units; delta is selected minus baseline in percentage points.', 'failure': 'Finite inputs required. Each comparison row may be unavailable on numeric overflow; other rows remain. Negative predictions are preserved and warned, including baseline.'}}

def pack(inputs):
    from copy import deepcopy
    import hashlib
    from pathlib import Path
    implementation = dict(status="content-hash", algorithm="sha256", runtime="python",
                          files={"run.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    return dict(schema=2, kind=MODEL_SPEC['id'], model=deepcopy(MODEL_SPEC), inputs=deepcopy(inputs), implementation=implementation, output=evaluate(inputs))


def unpack(payload):
    if (payload.get('schema') != 2 or payload.get('kind') != MODEL_SPEC['id'] or
            payload.get('model', {}).get('id') != MODEL_SPEC['id'] or
            payload.get('model', {}).get('version') != MODEL_SPEC['version']):
        raise ValueError('unsupported model/schema version')
    evaluate(payload['inputs'])
    return payload['inputs']


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
    denominator = sum(y)
    if not finite(denominator):
        raise ValueError('denominator overflow')
    rows = []
    for name, route, strength in [('baseline', 'Skip', 0), ('always', 'Basic', 1),
                                  ('selected', 'Skip' if inputs['route'] == 'Skip' else 'Basic', g)]:
        prediction = None
        try:
            prediction = correct(b, route, a, level, strength)
            if not all(finite(v) for v in prediction):
                raise ValueError('prediction overflow')
            errors = [abs(v-p) for v,p in zip(y,prediction)]
            total = sum(errors)
            score = None if denominator == 0 else 100*(total/denominator)
            if not finite(total) or (score is not None and not finite(score)):
                raise ValueError('metric overflow')
            rows.append(dict(name=name, status='ok', prediction=prediction, errors=errors,
                             error_sum=total, denominator=denominator, mae=total/7, wmape=score,
                             issue=None))
        except (OverflowError, ValueError):
            if prediction is not None and not all(finite(v) for v in prediction):
                prediction = None
            rows.append(dict(name=name, status='unavailable', prediction=prediction, errors=None,
                             error_sum=None, denominator=denominator, mae=None, wmape=None,
                             issue='finite_range_exceeded'))
    baseline = rows[0]['wmape']
    for row in rows:
        row['delta_pp'] = None if baseline is None or row['wmape'] is None else row['wmape']-baseline
    return dict(rows=rows, route=inputs['route'],
                negative_prediction=any(v < 0 for row in rows for v in (row['prediction'] or [])))


def reference_cases():
    default = dict(base=[10]*7, actual=[20]*7, additive=[0]*7, level=[math.log(2)]*7, gate=.5, route='Correct')
    return dict(model=MODEL_SPEC, inputs=default, output=evaluate(default))


if __name__ == '__main__':
    import argparse, json
    from pathlib import Path
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path)
    args = parser.parse_args()
    if args.input:
        payload = json.loads(args.input.read_text())
        print(json.dumps(evaluate(unpack(payload)), ensure_ascii=False, allow_nan=False, indent=2))
        raise SystemExit(0)

    import json
    from pathlib import Path
    result=experiment()
    result['reference'] = reference_cases()
    result['note']='教育用の人工例。原論文の学習・性能・本番効果は再現していない。'
    result['verification']={'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))

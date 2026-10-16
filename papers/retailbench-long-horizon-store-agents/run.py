"""Deterministic teaching experiment; not the RetailBench simulator or an LLM run."""
import json
import math
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def simulate(quality_aware, active_products, days=30):
    # Artificial two suppliers; identical demand, shelf capacity, and rent.
    unit_cost, return_rate = (4, 0.3) if not quality_aware else (5, 0.05)
    cash = 3000.0
    trace = []
    for day in range(1, days + 1):
        # Ten units of demand per managed product; at most 40 shelf positions.
        sold = min(active_products, 40) * 10
        revenue = sold * 10 * (1 - return_rate)
        procurement = sold * unit_cost
        cash += revenue - procurement - 600
        trace.append({'day': day, 'cash': round(cash, 2), 'sold': sold})
    return {'supplier': 'QualityFirst' if quality_aware else 'PriceFirst',
            'final_cash': round(cash, 2), 'trace': trace}


MODEL_SPEC = {'id': 'retailbench-local-accounting', 'version': '2.0.0', 'source': {'url': 'https://arxiv.org/html/2603.16453v3', 'version': 'arXiv:2603.16453v3'}, 'conventions': {'money': 'Input JSON numbers interpreted by canonical decimal value; exact rational monetary transitions internally; no affordability epsilon or cent rounding. Display/export numbers are rounded to binary64; inputs are recomputed on import.', 'accounting': 'Unlimited borrowing; daily q*(p*(1-r)-c)-rent; no stop at negative cash.', 'funded': 'Integer demand, positive cost; floor(exact cash/cost) capped by demand; prepay, same-day delivery/sale/refund, then rent; negative closing cash stops next-day transactions and rent.', 'returns': 'Same-day full refunds, returned stock discarded, zero lead time and carryover; fractional returned units are expectations. Zero sales return ratio undefined.', 'boundary': 'p*(r_A-r_B)=c_B-c_A describes accounting unit-margin tie only; price zero threshold undefined; local cash is not paper net worth or survival.'}}

def pack(inputs):
    from copy import deepcopy
    return dict(schema=2, kind=MODEL_SPEC['id'], model=deepcopy(MODEL_SPEC), inputs=deepcopy(inputs), output=evaluate(inputs))


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
    for key in ('price', 'demand', 'rent', 'cash', 'days', 'cost_a', 'cost_b', 'return_a', 'return_b'):
        if not finite(inputs.get(key)):
            raise ValueError(key + ': finite number required')
    if inputs.get('mode') not in ('accounting', 'funded'):
        raise ValueError('unknown mode')
    if not 1 <= inputs['days'] <= 365 or int(inputs['days']) != inputs['days']:
        raise ValueError('days must be integer 1..365')
    if any(inputs[k] < 0 for k in ('price', 'demand', 'rent', 'cash', 'cost_a', 'cost_b')):
        raise ValueError('negative input')
    if any(not 0 <= inputs[k] <= 1 for k in ('return_a', 'return_b')):
        raise ValueError('return rate outside 0..1')
    if inputs['mode'] == 'funded' and (inputs['demand'] != int(inputs['demand']) or min(inputs['cost_a'], inputs['cost_b']) <= 0):
        raise ValueError('funded mode requires integer demand and positive costs')
    # Canonical decimal values, exact internally: no budget epsilon or cents rounding.
    exact = lambda value: Fraction(str(value))
    p, q, rent = (exact(inputs[k]) for k in ('price', 'demand', 'rent'))
    suppliers = []
    for label in ('a', 'b'):
        c, rate = exact(inputs['cost_'+label]), exact(inputs['return_'+label])
        cash = exact(inputs['cash']); trace = []; stopped = None
        for day in range(1, int(inputs['days'])+1):
            before = cash
            active = stopped is None
            sold = (math.floor(min(q, max(cash, 0)/c)) if inputs['mode'] == 'funded' else q) if active else 0
            purchase, gross, refund, fee = sold*c, sold*p, sold*p*rate, rent if active else 0
            cash = before-purchase+gross-refund-fee
            if not finite(float(cash)):
                raise ValueError('cash overflow')
            money = dict(opening=before, purchased=sold, purchase=purchase, gross=gross, refund=refund,
                         rent=fee, sold=sold, lost=q-sold if active else 0, expected_returns=sold*rate, cash=cash)
            trace.append(dict(day=day, active=active, **{k: float(v) for k,v in money.items()},
                              return_ratio=float(rate) if sold else None))
            if inputs['mode'] == 'funded' and stopped is None and cash < 0:
                stopped = day
        suppliers.append(dict(supplier=label.upper(), margin=float(p*(1-rate)-c), final_cash=float(cash), stopped=stopped, trace=trace))
    p = inputs['price']
    threshold = None if p == 0 else inputs['return_a']-(inputs['cost_b']-inputs['cost_a'])/p
    difference = p*(inputs['return_a']-inputs['return_b'])-(inputs['cost_b']-inputs['cost_a'])
    if (threshold is not None and not finite(threshold)) or not finite(difference):
        raise ValueError('boundary overflow')
    return dict(suppliers=suppliers, return_b_tie=threshold, margin_difference=difference)


def reference_cases():
    default = dict(price=10, demand=200, rent=600, cash=3000, days=30,
                   cost_a=4, cost_b=5, return_a=.3, return_b=.05, mode='accounting')
    return dict(model=MODEL_SPEC, inputs=default, output=evaluate(default))


def main():
    reported = [
        ['DeepSeek-V4-Pro', 'Plan-and-Act', 180, 10120.90, 164417],
        ['GLM-5.1', 'ReAct', 60, -2134.36, 7016],
        ['GPT-5.5', 'ReAct', 180, 24350.98, 136405],
        ['Grok-4.3', 'ReAct', 58, 828.40, 11305],
        ['Kimi-K2.6', 'ReAct', 130, 792.19, 86214],
        ['MiniMax-M2.5', 'Plan-and-Act', 73, -397.95, 23521],
        ['Qwen3.5-397B-A17B', 'Reflection', 71, 1183.17, 35622],
        ['Oracle Policy', 'Oracle', 180, 131510.42, 267998],
    ]
    frames = [{'products': n, 'policies': [simulate(False, n), simulate(True, n)]} for n in [1, 8, 20, 38]]
    assert all(f['policies'][1]['final_cash'] > f['policies'][0]['final_cash'] for f in frames)
    # Independent accounting identity, across every simulated day and setting.
    for f in frames:
        for p in f['policies']:
            margin = 4.5 if p['supplier'] == 'QualityFirst' else 3
            assert all(abs(t['cash'] - (3000 + t['day'] * (f['products']*10*margin-600))) < 1e-8 for t in p['trace'])
    result = {'lab30_retailbench': True, 'status': 'PARTIAL',
              'source': {'paper': '2603.16453v3', 'locator': 'Table 1; Sections 5.2–5.3; Figure 3'},
              'reported_columns': ['model', 'framework', 'days', 'net_worth', 'sales_units'],
              'reported': reported, 'frames': frames, 'reference': reference_cases(),
              'verification': {'accounting_identity': 'CONFIRMED', 'retailbench_reproduction': 'NOT TESTED'},
              'limitations': ['Artificial deterministic inputs; no LLM, lead time, aging, or news. Legacy frames and accounting mode do not stop at negative cash; funded mode uses a local immediate-stop rule, not the paper rule.', 'Final cash is not paper net worth; return rates are invented teaching assumptions.']}
    (ROOT/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print('CONFIRMED: 240 daily accounting checks; RetailBench performance NOT TESTED')

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

    main()

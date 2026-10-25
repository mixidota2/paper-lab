"""Independent direct-demand oracle; synthetic values only. Run with uv run."""
import itertools
import json
from pathlib import Path

ITEMS = [
    dict(id='A1', category='A', brand='A赤', q=12, p=4, w=1, d=4),
    dict(id='A2', category='A', brand='A赤', q=8, p=6, w=1, d=2),
    dict(id='A3', category='A', brand='A青', q=4, p=3, w=1, d=6),
    dict(id='B1', category='B', brand='B赤', q=10, p=5, w=1, d=3),
    dict(id='B2', category='B', brand='B青', q=6, p=4, w=1, d=6),
    dict(id='B3', category='B', brand='B青', q=3, p=8, w=1, d=2),
]
DEFAULT = dict(capacity=5, s=.4, beta=.25, r=4, c=2, e=.5, brands=1)
CAPACITIES = (1, 2, 3, 4)
EPS = 1e-9


def evaluate(items, faces, p):
    selected = [(x, f) for x, f in zip(items, faces) if f]
    total = sum(x['q'] for x in items)
    base = sum(x['q'] for x, f in selected)
    if not base or base + EPS < p['e'] * total:
        return None
    if not p['brands'] <= len({x['brand'] for x, f in selected}) <= 2:
        return None
    rows = []
    for x, f in selected:
        direct = x['q'] * f ** p['beta']
        transfer = p['s'] * x['q'] * (total-base) / base
        demand = direct + transfer
        rows.append(dict(id=x['id'], faces=f, direct=direct, transfer=transfer,
                         demand=demand, gross=demand*x['p'],
                         replenishment=p['r']*demand/(f*x['d']), fixed=p['c']))
    profit = sum(x['gross']-x['replenishment']-x['fixed'] for x in rows)
    return dict(faces=list(faces), used=sum(x['w']*f for x, f in selected),
                profit=profit, unmet_base=total-base, lost=(1-p['s'])*(total-base), rows=rows)


def eq4(items, faces, p):
    selected = [(x, f) for x, f in zip(items, faces) if f]
    base = sum(x['q'] for x, f in selected)
    y = sum(x['q']*(x['p']-p['r']/(f*x['d'])) for x, f in selected)/base
    first = sum(x['q']*(f**p['beta']-p['s'])*(x['p']-p['r']/(f*x['d']))-p['c'] for x, f in selected)
    return first + p['s']*sum(x['q'] for x in items)*y


def oracle(p, capacities=CAPACITIES):
    """No category value table: inspect all 729 joint face vectors directly."""
    best = None
    ties = []
    for faces in itertools.product(range(3), repeat=6):
        cats = [evaluate(ITEMS[j:j+3], faces[j:j+3], p) for j in (0, 3)]
        if any(x is None for x in cats):
            continue
        allocation = [next((s for s in sorted(capacities) if s >= x['used']), None) for x in cats]
        if None in allocation or sum(allocation) > p['capacity']:
            continue
        profit = sum(x['profit'] for x in cats)
        record = dict(profit=profit, faces=list(faces), allocation=allocation, categories=cats)
        if best is None or profit > best['profit'] + EPS:
            best, ties = record, [list(faces)]
        elif abs(profit-best['profit']) <= EPS:
            ties.append(list(faces))
    if best:
        best['optimal_face_vectors'] = ties
        best['optimal_face_count'] = len(ties)
    return best


def main():
    cases = [('default', DEFAULT), ('degenerate_ties', dict(DEFAULT, capacity=8, s=0, beta=0, r=0, c=0))]
    for key, values in dict(capacity=range(2, 9), s=[0, 1], beta=[0, 1], r=[0, 12], c=[0, 10], e=[0, 1], brands=[2]).items():
        cases.extend((f'{key}={value}', dict(DEFAULT, **{key:value})) for value in values)
    result = dict(model_version='shelf-decomposition-2',lab_kind='storewide-shelf-decomposition',
                  note='全て合成値。原論文の計算表・実店舗の効果は再現していない。',
                  inputs=ITEMS, defaults=DEFAULT, capacity_candidates=CAPACITIES,
                  cases=[dict(name=name, parameters=p, oracle=oracle(p)) for name, p in cases],
                  printed_equation_fixture=dict(direct=15, equation4=15, printed_equation2=25),
                  verification=dict(mechanism='PARTIAL', performance='NOT TESTED', scaling='NOT TESTED', production_applicability='NOT TESTED'))
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result['cases'][0]['oracle'], ensure_ascii=False))


if __name__ == '__main__':
    main()

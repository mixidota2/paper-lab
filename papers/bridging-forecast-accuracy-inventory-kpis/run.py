"""Small explanatory counterexample, NOT the TruckParts experiment."""
import json
import math
import random
from pathlib import Path

REPORTED = [
    ['XGBoost', .43, 820000], ['Random Forest', .43, 750000],
    ['SVR', .50, 840000], ['ARIMA', .53, 750000],
    ['Croston', .52, 740000], ['SBA', .51, 780000], ['TSB', .57, 780000],
]


def croston(train, alpha=.1):
    size, interval, gap = None, None, 0
    for demand in train:
        gap += 1
        if demand:
            if size is None:
                size, interval = demand, gap
            else:
                size += alpha * (demand - size)
                interval += alpha * (gap - interval)
            gap = 0
    return size / interval if size is not None else 0.


def simulate(demand, forecast, penalty):
    # Identical policy for both forecasts: one-day replenishment, target ceil(5*f).
    target = math.ceil(5 * forecast)
    stock = incoming = held = lost = served = ordered = 0
    trace = []
    for d in demand:
        before = stock
        arrival = incoming
        stock += arrival
        sold = min(stock, d)
        stock -= sold
        shortage = d - sold
        incoming = max(0, target - stock)
        assert stock == before + arrival - sold
        assert d == sold + shortage
        held += stock
        lost += shortage
        served += sold
        ordered += incoming
        trace.append(stock)
    assert served + lost == sum(demand)
    return {'forecast': round(forecast, 6), 'target': target,
            'mae': round(sum(abs(d - forecast) for d in demand) / len(demand), 6),
            'holding': held, 'lost': lost, 'served': served,
            'cost': held + penalty * lost,
            'fill_rate': round(served / sum(demand), 6), 'trace': trace[:60]}


def main():
    rng = random.Random(260101)
    series = [4 if rng.random() < .1 else 0 for _ in range(1095)]
    train, test = series[:730], series[730:]
    forecast = croston(train)
    frames = []
    for penalty in [1, 5, 20, 50]:
        rows = [dict(model=name, **simulate(test, f, penalty))
                for name, f in [('Zero', 0.), ('Croston', forecast)]]
        frames.append({'penalty': penalty, 'rows': rows})
    assert frames[-1]['rows'][0]['mae'] < frames[-1]['rows'][1]['mae']
    assert frames[-1]['rows'][0]['cost'] > frames[-1]['rows'][1]['cost']
    result = {'lab01_forecast': True, 'reported_source': '2601.21844v2 Table 1 (rounded)',
              'reported': REPORTED, 'frames': frames, 'seed': 260101,
              'train_days': 730, 'test_days': 365, 'test_demand': sum(test),
              'verification': {'mechanism': 'PARTIAL', 'performance': 'NOT TESTED',
                               'scaling': 'NOT TESTED', 'production_applicability': 'NOT TESTED'},
              'checks': {'stock_conservation': 'CONFIRMED', 'demand_conservation': 'CONFIRMED',
                         'toy_rank_inversion_penalty_50': 'CONFIRMED'},
              'boundary': 'Independent Bernoulli demand; simplified lost-sales policy; no official simulator or tree models.'}
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps([{ 'penalty': f['penalty'], 'rows': [{k:v for k,v in r.items() if k != 'trace'} for r in f['rows']]} for f in frames], indent=2))


if __name__ == '__main__':
    main()

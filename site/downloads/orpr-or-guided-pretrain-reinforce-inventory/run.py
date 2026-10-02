"""ORPR §3.3 label generation, reduced to two deterministic categories.

No Transformer/VAE training or RL performance reproduction. Standard library only.
"""
import itertools
import json
from pathlib import Path


def replay(demand, days, review=3, lead=1):
    """Order-up-to days of mean demand; arrivals precede sales; lost sales vanish."""
    mean = sum(demand) / len(demand)
    target = mean * days
    inventory = 0.0
    pipeline = {}
    stock = lost = served = ordered = 0.0
    trace = []
    for t, d in enumerate(demand):
        inventory += pipeline.pop(t, 0)
        if t % review == 0:
            q = max(0, target - inventory - sum(pipeline.values()))
            pipeline[t + lead] = pipeline.get(t + lead, 0) + q
            ordered += q
        sale = min(inventory, d)
        inventory -= sale
        served += sale
        lost += d - sale
        stock += inventory
        trace.append(round(inventory, 5))
    assert abs(served + lost - sum(demand)) < 1e-9
    assert abs(ordered - served - inventory - sum(pipeline.values())) < 1e-9
    return dict(stock=stock, loss=lost, served=served, trace=trace)


def rloo(rewards):
    return [r - (sum(rewards) - r) / (len(rewards) - 1) for r in rewards]


def main():
    demand = [[3, 2, 4, 3, 3, 5, 8, 9, 7, 3, 2, 3],
              [1, 2, 1, 2, 3, 2, 4, 5, 3, 2, 1, 2]]
    tables = [[replay(d, v) for v in range(1, 11)] for d in demand]
    candidates = []
    for a, b in itertools.product(range(10), repeat=2):
        candidates.append(dict(days=[a+1, b+1], stock=tables[0][a]['stock'] + tables[1][b]['stock'],
                               loss=tables[0][a]['loss'] + tables[1][b]['loss']))
    sale = sum(map(sum, demand))  # Fixed reference sales denominator for this toy.
    cases = []
    for alpha in [.70, .80, .90, .95, .98]:
        budget = sale * (1-alpha)
        feasible = [c for c in candidates if c['loss'] <= budget + 1e-9]
        best = min(feasible, key=lambda c: (c['stock'], c['loss'], c['days'])) if feasible else None
        cases.append(dict(alpha=alpha, budget=budget, feasible=len(feasible), best=best))
    assert cases[0]['best']['stock'] <= cases[1]['best']['stock'] <= cases[2]['best']['stock']
    rewards = [-9, -6, -3, -2]
    advantages = rloo(rewards)
    assert abs(sum(advantages)) < 1e-9
    assert all(abs(a-b) < 1e-12 for a, b in zip(rloo([r+10 for r in rewards]), advantages))
    result = dict(lab02='orpr', note='合成需要のORラベルとRLOO基準値だけを検算。著者の学習・現場評価は再現していない。',
                  cases=cases, candidates=candidates, rewards=rewards, advantages=advantages,
                  paper_evidence={'offline_total_cost': {'JD online': 3491, 'ORPR': 3153},
                    'field': {'psm': [-5.27, 2.29, -29.95], 'did': [-4.07, .47, -18.35]},
                    'holding_yoy': [22.05, 3.7], 'parameters_million': .93},
                  experiments=[dict(name='ORラベルとleave-one-out基準値', metrics={
                      '候補組合せ': len(candidates), '需要合計': sale,
                      '制約を満たす候補数': [c['feasible'] for c in cases],
                      'RLOO advantage合計': sum(advantages)})])
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()

"""2カテゴリの架空の需要を使い、補充量の目安と報酬差を計算する。

TransformerやVAEの学習、強化学習後の性能は再現しない。標準ライブラリだけで動く。
"""
import itertools
import json
from pathlib import Path


def replay(demand, days, review=3, lead=1):
    """需要の平均から目標在庫を決める。入荷は販売より先で、売り逃しは翌日に繰り越さない。"""
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
    sale = sum(map(sum, demand))  # 論文の実売上SALEではなく、この人工例では需要の合計を固定して使う。
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
    result = dict(lab02='orpr', note='架空の需要から補充の候補を比べ、候補ごとの報酬差を求めます。論文の学習や現場評価は再現していません。',
                  cases=cases, candidates=candidates, rewards=rewards, advantages=advantages,
                  paper_evidence={'offline_total_cost': {'JD online': 3491, 'ORPR': 3153},
                    'field': {'psm': [-5.27, 2.29, -29.95], 'did': [-4.07, .47, -18.35]},
                    'holding_yoy': [22.05, 3.7], 'parameters_million': .93},
                  experiments=[dict(name='売り逃しの上限を守る補充案と、候補間の報酬差', metrics={
                      '候補組合せ': len(candidates), '需要合計': sale,
                      '制約を満たす候補数': [c['feasible'] for c in cases],
                      'RLOO advantage合計': sum(advantages)})])
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()

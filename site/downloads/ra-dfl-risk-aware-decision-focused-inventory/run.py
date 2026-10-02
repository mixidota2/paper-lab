"""Enumerated two-channel mean-CVaR allocation and rho=0 masked-loss check.

Not RA-DFL training. No neural model, data imputation or differentiable solver.
"""
import json
from pathlib import Path


def cost(q, d, rho=.4, h=1, b=6, tau=1):
    surplus = sum(max(a-z, 0) for a, z in zip(q, d))
    shortage = sum(max(z-a, 0) for a, z in zip(q, d))
    # Equal positive h,b and tau<h+b, so all feasible recourse is beneficial.
    moved = min(surplus, rho*shortage)
    return h*surplus + b*shortage - (h+b-tau)*moved


def cvar(values, alpha=.8):
    # Exact finite equiprobable Rockafellar–Uryasev representation, including ties.
    return min(eta + sum(max(v-eta, 0) for v in values)/len(values)/(1-alpha)
               for eta in values)


def evaluate(q, scenarios):
    values = [cost(q, d) for d in scenarios]
    return dict(mean=sum(values)/len(values), tail=cvar(values))


def main():
    scenarios = [(2, 3)]*6 + [(8, 2)]*2 + [(2, 10)]*2
    cases = []
    for weight in [0, .25, .5, .75, 1]:
        candidates = []
        for a in range(11):
            for b in range(11-a):
                metrics = evaluate((a, b), scenarios)
                objective = (1-weight)*metrics['mean'] + weight*metrics['tail']
                candidates.append(dict(q=[a, b], objective=objective, **metrics))
        best = min(candidates, key=lambda c: (c['objective'], c['mean'], c['q']))
        cases.append(dict(weight=weight, best=best, candidates=candidates))
    checks = 0
    curves = []
    # rho=0 only: check masked cost <= true cost for every y<=D in this grid.
    for d in range(13):
        for y in range(d+1):
            for q in range(16):
                masked = 6*max(y-q, 0)
                true = max(q-d, 0)+6*max(d-q, 0)
                assert masked <= true
                checks += 1
    for q in range(16):
        curves.append(dict(q=q, naive=max(q-4, 0)+6*max(4-q, 0),
                           masked=6*max(4-q, 0), true=max(q-10, 0)+6*max(10-q, 0)))
    assert abs(cvar([1, 2, 3, 4, 5], .8)-5) < 1e-9
    result = dict(lab02='radfl', note='合成2チャネルの配分を全探索。RA-DFLの学習やPTO悪化の再現ではない。打切り検算は横持ちなしに限定。',
                  cases=cases, censoring=curves,
                  paper_evidence={'m5': {'LightGBM-QR PTO': [4.903, 13.70], 'PTO + CVaR': [5.380, 14.36],
                    'DFL-EV': [4.690, 14.11], 'RA-DFL': [4.721, 13.67]},
                    'censoring': {'M5': {'proxy_rate': 12.3, 'full': 4.721, 'without_mask': 4.776, 'p': .003},
                                  'Stallion': {'proxy_rate_table1': 1.3, 'proxy_rate_section58': 1.4, 'p': .25}}},
                  experiments=[dict(name='配分と打切り損失の限定検算', metrics={
                      '容量': 10, '各リスク重みの候補数': 66, '下界の照合数': checks,
                      '平均重視の配分': cases[0]['best']['q'], '裾重視の配分': cases[-1]['best']['q']})])
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()

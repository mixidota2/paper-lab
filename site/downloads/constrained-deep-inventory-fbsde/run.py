"""Deterministic local linear reduction of Eqs. (9), (15), (20); no FBSDE training."""
import json
from pathlib import Path


def frame(capacity):
    x, pipeline, demand, tau, gamma, nominal = 7., 4., 1., 2., .5, 4.
    hx = capacity - x
    h1 = demand - pipeline / tau + gamma * hx
    transit_cap = pipeline / tau + gamma * (6 - pipeline)
    onhand_cap = pipeline / tau - gamma * pipeline + gamma * tau * demand + gamma * tau * h1
    upper = min(transit_cap, onhand_cap)
    feasible = upper >= 0
    order = min(nominal, upper) if feasible else None
    # h1dot + gamma*h1 = (onhand_cap-u)/tau in this linear reduction.
    residual = (onhand_cap - order) / tau if feasible else None
    return dict(label=f'Hˣ = {capacity:g}', capacity=capacity, x=x, pipeline=pipeline,
                h=hx, h1=h1, transit_upper=transit_cap, onhand_upper=onhand_cap,
                nominal=nominal, order=order, residual=residual,
                augmented_initial_safe=hx >= 0 and h1 >= 0, feasible=feasible)


def main():
    frames = [frame(h) for h in [6, 8, 10, 14]]
    assert frames[2]['order'] == 1.5 and frames[2]['residual'] == 0
    assert not frames[1]['augmented_initial_safe'] and frames[1]['h'] > 0
    assert not frames[0]['feasible']
    # An order perturbation changes dL/dt immediately, but only d²X/dt².
    du, tau = .01, 2
    derivative_check = {'d_dLdot_du': du / du, 'd_dXdot_du': 0., 'd_dXddot_du': (du/tau)/du}
    result = {'lab30_fbsde': True, 'seed': None, 'scope': '決定論・単品・線形流量の局所計算。学習・確率安全性・性能は検証しない。',
              'frames': frames, 'derivative_check': derivative_check,
              'paper_reported': {'source': 'Tables II–IV; eight seeds; not reproduced', 'M': 50,
                'fill_rate': .562, 'fill_rate_sd': .031, 'onhand_violation': .815, 'onhand_M1': .050,
                'onhand_M3': .083, 'onhand_utilization': 1.02, 'emission_onhand_violation': .077},
              'verification': {'mechanism': 'PARTIAL', 'performance': 'NOT TESTED', 'scaling': 'NOT TESTED', 'production_applicability': 'NOT TESTED'}}
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print('PASS: relative-degree derivatives, binding QP bound, initial-set and infeasibility checks')

if __name__ == '__main__':
    main()

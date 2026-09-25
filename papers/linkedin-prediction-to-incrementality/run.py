"""Exact tiny allocation example; no fitted causal model or production data."""
import itertools
import json
from pathlib import Path

# mu0 and mu1 are stipulated potential-outcome means, not estimates.
ROWS = [
    {"user": "A", "mu0": .90, "mu1": .85, "cost": 1},
    {"user": "B", "mu0": .65, "mu1": .70, "cost": 1},
    {"user": "C", "mu0": .10, "mu1": .40, "cost": 2},
    {"user": "D", "mu0": .05, "mu1": .25, "cost": 1},
]

def allocate(score, budget):
    feasible = [x for x in itertools.product((0, 1), repeat=4)
                if sum(r['cost'] * a for r, a in zip(ROWS, x)) <= budget]
    x = max(feasible, key=lambda x: sum(score(r) * a for r, a in zip(ROWS, x)))
    return {"selected": [r['user'] for r, a in zip(ROWS, x) if a],
            "cost": sum(r['cost'] * a for r, a in zip(ROWS, x)),
            "incremental_value": round(sum((r['mu1']-r['mu0']) * a for r, a in zip(ROWS, x)), 6) + 0.0,
            "expected_total_outcome": round(sum(r['mu0'] + (r['mu1']-r['mu0']) * a for r, a in zip(ROWS, x)), 6)}

def compute():
    cases = {str(b): {"response": allocate(lambda r: r['mu1'], b),
                     "incremental": allocate(lambda r: r['mu1']-r['mu0'], b)} for b in (2, 3, 5)}
    assert cases['3']['response']['selected'] == ['A', 'B', 'D']
    assert cases['3']['incremental']['selected'] == ['C', 'D']
    assert all('A' not in c['incremental']['selected'] for c in cases.values())
    assert cases['5']['incremental']['cost'] == 4  # budget need not be exhausted
    return {"note": "既知の反実仮想平均を与えた人工例。学習・探索・LP緩和の再現ではない。",
            "verification": {"mechanism": "PARTIAL", "performance": "NOT TESTED", "scaling": "NOT TESTED", "production_applicability": "NOT TESTED"},
            "rows": ROWS, "budgets": cases,
            "checks": {"negative_effect_withheld": "CONFIRMED", "capacity_changes_allocation": "CONFIRMED", "dual_solver": "NOT TESTED", "last_layer_LLA": "NOT TESTED"}}

if __name__ == '__main__':
    result = compute()
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))

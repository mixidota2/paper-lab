"""Independent checks for the small inventory mechanisms, not paper performance."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(slug):
    spec = importlib.util.spec_from_file_location('toy', ROOT/'papers'/slug/'run.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_lost_sales_accounting_and_rloo_baseline():
    m = load('orpr-or-guided-pretrain-reinforce-inventory')
    assert m.replay([0]*12, 5)['stock'] == 0
    assert m.replay([2]*12, 0)['loss'] == 24
    assert m.rloo([5, 5, 5]) == [0, 0, 0]
    assert m.rloo([1, 4]) == [-3, 3]
    for days in range(1, 11):
        result = m.replay([0, 2, 8, 1, 2, 4], days)
        assert result['loss'] + result['served'] == pytest.approx(17)
        assert min(result['trace']) >= 0


def test_quadratic_counterexample_and_state_kkt():
    m = load('proximal-residual-value-inventory-placement')
    assert m.path('counterexample', 1)[-1] == [2, 0]
    assert m.path('counterexample', 2)[-1] == [1, 1]
    # Direct objective evaluation independently checks the bisection solver.
    for state in [[0, 0], [.2, 1], [2, 3]]:
        for budget in [.1, 1, 3]:
            x = m.allocate(state, budget, 'state')
            def value(x):
                return abs(x[0]-.5)+2*abs(x[1]-3)+sum(v*v/2 for v in x)
            for j in range(101):
                y = [state[0]+budget*j/100, state[1]+budget*(1-j/100)]
                assert value(x) <= value(y)+1e-10
    assert m.path('state', 1)[-1] == pytest.approx(m.path('state', 500)[-1])
    assert m.path('action', 1)[-1] != pytest.approx(m.path('action', 2)[-1])


def test_cvar_fractional_tail_and_recourse():
    m = load('ra-dfl-risk-aware-decision-focused-inventory')
    # Worst 1.5 of three equally weighted scenarios: (9 + .5*3) / 1.5.
    assert m.cvar([0, 3, 9], .5) == pytest.approx(7)
    assert m.cvar([0, 3, 9], 0) == pytest.approx(4)
    assert m.cost([4, 4], [4, 4]) == 0
    assert m.cost([10, 0], [0, 10], rho=0) == 70
    assert m.cost([10, 0], [0, 10], rho=1) == 10
    assert m.cost([10, 0], [0, 10], rho=.4) == 46

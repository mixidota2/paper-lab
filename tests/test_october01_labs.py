"""Independent invariants for the limited October 1 mechanism experiments."""
import importlib.util
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(slug):
    spec = importlib.util.spec_from_file_location('toy', ROOT / 'papers' / slug / 'run.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_remapping_representability_with_signed_inventory():
    m = module('deepstock-policy-regularized-inventory-drl')
    for inventory in [-20, 0, 10, 100]:
        for q in [0, .25, 10, 1000]:
            assert m.action('Base', inventory, [q + inventory], []) == q
            assert m.action('Both', inventory, [0, q + inventory], [8, 1]) == q
            assert m.action('Coeff', inventory, [0, q], [8, 1]) == q


def test_projection_satisfies_variational_inequality():
    m = module('diff-projection-feasible-multi-echelon-inventory')
    rng = random.Random(1001)
    # For a convex feasible set, this inequality characterizes metric projection.
    for _ in range(150):
        z = [rng.uniform(-5, 12), rng.uniform(-5, 12)]
        x = m.project(z)
        assert m.feasible(x)
        for _ in range(25):
            y0 = rng.uniform(0, 3)
            y = [y0, rng.uniform(0, 6-y0)]
            assert sum((z[i]-x[i])*(y[i]-x[i]) for i in range(2)) <= 1e-8
        floor, integer = m.integer_map(x, z)
        assert m.feasible(integer)
        assert all(v == int(v) for v in integer)
        assert m.objective(integer, z) <= m.objective(floor, z) + 1e-8


def test_inventory_accounting_and_cost_sensitivity():
    m = module('bridging-forecast-accuracy-inventory-kpis')
    d = [0, 0, 4, 0, 4, 0, 0, 4]
    cheap = m.simulate(d, .8, 1)
    expensive = m.simulate(d, .8, 21)
    assert cheap['served'] + cheap['lost'] == sum(d)
    assert expensive['cost'] - cheap['cost'] == 20 * cheap['lost']
    assert expensive['mae'] == cheap['mae']
    assert expensive['fill_rate'] == cheap['fill_rate']
    zero = m.simulate(d, 0, 1)
    assert zero['lost'] == sum(d) and zero['holding'] == 0
    assert m.croston([0]*10) == 0

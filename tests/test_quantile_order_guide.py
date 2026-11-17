"""Execute the actual guide snippet, not a second implementation."""
from pathlib import Path
import re
from fractions import Fraction as F

ROOT = Path(__file__).resolve().parents[1]

def example():
    text = (ROOT / 'guides/forecast-to-replenishment.md').read_text()
    snippets = re.findall(r'```python\n(.*?)```', text, re.S)
    code, = [s for s in snippets if s.startswith('# quantile-order-example:')]
    ns = {}
    exec(compile(code, 'guide-example', 'exec'), ns)
    return ns

def test_expected_table_and_feasible_optimum():
    ns = example()
    for q, excess, shortage, cost in [
        (9, F(12,5), F(11,5), F(9)),
        (8, F(8,5), F(12,5), F(44,5)),
        (6, F(4,5), F(18,5), F(58,5)),
        (12, F(24,5), F(8,5), F(48,5)),
    ]:
        assert ns['quantities'](q) == (excess, shortage)
        assert ns['cost'](q) == cost
    assert ns['cost'](8) == min(ns['cost'](q) for q in range(31))
    assert ns['best_lot'] == 12
    assert ns['cost'](12) == min(ns['cost'](q) for q in ns['feasible'])

def test_service_denominators_and_reversed_costs():
    ns = example()
    assert sum(p for d,p in ns['demand'] if d <= 8) == F(4,5)
    assert 1 - ns['quantities'](8)[1] / ns['mean'] == F(8,11)
    # Reversing the costs changes the best decision under the same demand.
    ns['overage_cost'], ns['underage_cost'] = F(3), F(1)
    assert min(range(31), key=ns['cost']) == 4
    assert ns['cost'](6) < ns['cost'](12)

"""Independent checks of the three limited mechanism experiments."""
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SLUGS=['sabreagent-design-time-inventory','or-transformer-joint-replenishment','switch-hurdle-intermittent-demand']

def module(slug):
    spec=importlib.util.spec_from_file_location('experiment',ROOT/'papers'/slug/'run.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m

def test_inventory_conservation_and_capped_limits():
    m=module(SLUGS[0])
    for stock in range(10):
        for d in range(10):
            end,lost,_=m.project(stock,[2],[d])
            assert end == max(stock+2-d,0)
            assert stock+2+lost == end+d
    for ip in range(20):
        assert 0<=m.capped(ip,4,3,1)<=4
        assert m.capped(ip,4,3,3)==max(12-ip,0)
    assert m.dp_check()['max_error']<1e-10

def test_closed_order_has_no_quantity_effect():
    m=module(SLUGS[1])
    assert m.cost(0,0)==m.cost(100,0)
    assert m.derivative(100,0)==0
    assert m.cost(4.5,1)>m.cost(4,1)
    assert m.experiment()['permutation']['max_error']<1e-12

def test_hurdle_extreme_occurrence_and_geometric_case():
    m=module(SLUGS[2])
    assert m.hurdle(0,0,2,1)==1
    assert m.hurdle(1,0,2,1)==0
    assert m.hurdle(0,1,2,1)==0
    # alpha=1 => geometric NB; positive conditional mean is mu+1.
    for mu in [1,2,4]:
        assert abs(sum(y*m.hurdle(y,1,mu,1) for y in range(1000))-(mu+1))<1e-10

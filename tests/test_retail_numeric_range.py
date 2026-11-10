"""Finite serialized output is distinct from an undefined zero denominator."""
from fractions import Fraction
from pathlib import Path
import importlib.util
import json
import math
import random
import subprocess

import unittest

P = Path(__file__).resolve().parents[1] / 'papers/retail-forecast-decision-grain'
spec = importlib.util.spec_from_file_location('grain_range', P / 'run.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def js(cases):
    script = r'''
const M=require(process.argv[1]);let input='';process.stdin.on('data',x=>input+=x);
process.stdin.on('end',()=>console.log(JSON.stringify(JSON.parse(input).map(c=>{
 try {const value=M[c.fn](...c.args);return {value,json:JSON.stringify(value)};}
 catch(e){return {error:e.name,message:e.message};}
}),(_,v)=>typeof v==='number'&&!Number.isFinite(v)?String(v):v)));
'''
    return json.loads(subprocess.run(['node', '-e', script, str(P/'model.js')],
        input=json.dumps(cases), text=True, capture_output=True, check=True).stdout)


def case(fn, *args):
    return {'fn': fn, 'args': args}


def test_js_positive_values_never_become_zero_denominator_null():
    cases = [case('metrics', [1e-200], [0], [1e-200], [1], [0]),
             case('metrics', [1], [0], [1], [5e-324], [0]),
             case('metrics', [1e-100], [0], [1], [1e-300], [0])]
    # First case loses price*actual, third loses weight*error. The middle
    # case is representable and must not be rejected merely for tiny weight.
    results = js(cases)
    assert results[0]['error'] == 'RangeError'
    assert results[1]['value'] == {'old': 1, 'corrected': 1}
    assert results[2]['error'] == 'RangeError'


def test_js_overflow_and_output_underflow_fail_before_serialization():
    cases = [case('windows', [1e-320], [1]),
             case('windows', [10000], [10000-1e-12]),
             case('metrics', [10000,0], [10000,5e-324], [1,1], [1,1], [0,1]),
             case('windows', [5e-324,5e-324], [5e-16,5e-16])]
    results = js(cases)
    assert results[0]['error'] == 'RangeError'
    assert results[1]['value']['mean'] > 0
    assert results[2]['error'] == 'RangeError'
    # Each ratio is finite but their sum overflows before averaging.
    assert results[3]['error'] == 'RangeError'


def test_python_rejects_output_underflow_and_overflow():
    for args in [([1e-320], [1]), ([1e308, 0], [1e308, 5e-324])]:
        with unittest.TestCase().assertRaises(ValueError):
            m.windows(*args)
    with unittest.TestCase().assertRaises(ValueError):
        m.metrics([1e308,0],[1e308,5e-324],[1,1],[1,1],[0,1])
    with unittest.TestCase().assertRaises(ValueError):
        m.loss('1e-400', 0, .5)
    assert m.finite_float(Fraction(0)) == 0
    assert m.finite_float(None) is None
    assert m.finite_float(Fraction('5e-324')) == 5e-324


def test_exact_zero_semantics_and_representable_tiny_results():
    cases = [case('metrics', [0],[1],[1],[0],[0]),
             case('metrics', [1],[1],[0],[1],[0]),
             case('windows', [0],[1]),
             case('windows', [0,1],[1,1]),
             case('metrics', [1e-150],[0],[1e-150],[1],[0]),
             case('metrics', [1],[1],[1],[5e-324],[0]),
             case('windows', [1e-320],[0])]
    results = js(cases)
    for c, observed in zip(cases, results):
        expected = getattr(m, c['fn'])(*c['args'])
        assert 'value' in observed, (c, observed)
        assert json.loads(observed['json']) == observed['value']
        for key, value in expected.items():
            actual = observed['value'][key]
            if value is None:
                assert actual is None
            else:
                assert isinstance(actual, (int, float)) and math.isfinite(actual)
                assert math.isclose(actual, value, rel_tol=2e-14, abs_tol=0)


def test_normal_scale_randomized_oracle_and_results_preservation():
    rng = random.Random(915)
    cases = []
    for _ in range(500):
        n = rng.randrange(1, 9)
        a = [rng.randrange(10001)/10 for _ in range(n)]
        f = [rng.randrange(10001)/10 for _ in range(n)]
        g = [rng.randrange(3) for _ in range(n)]
        prices = [rng.randrange(5) for _ in range(3)]
        cases.append(case('metrics', a, f, [prices[i] for i in g],
                          [rng.randrange(5) for _ in range(n)], g))
    for _ in range(100):
        cases.append(case('windows', [rng.randrange(100) for _ in range(3)],
                          [rng.randrange(100) for _ in range(3)]))
    for r in (.5,.8,.95):
        for q in (0,8,10,12,10000):
            for y in (0,10,10000):
                cases.append(case('loss', q, y, r))
    for c, observed in zip(cases, js(cases)):
        expected = getattr(m,c['fn'])(*c['args'])
        assert 'value' in observed, (c, observed)
        values = expected.items() if isinstance(expected,dict) else [('loss',expected)]
        for key,value in values:
            actual = observed['value'][key] if isinstance(expected,dict) else observed['value']
            if value is None:
                assert actual is None
            else:
                assert math.isfinite(actual)
                assert math.isclose(actual,value,rel_tol=1e-12,abs_tol=1e-12)
    assert m.results()['zero_sales'] == {
        'A': {'old':500000000.05,'corrected':.11},
        'B': {'old':.1,'corrected':.2}}
    assert [row['loss'] for row in m.results()['order_loss']] == [2,0,2,8,0,2,38,0,2]


def test_known_numeric_limits_are_explicit_not_universal_parity():
    # JS rejects an unrepresentable intermediate product; Fraction-based
    # Python can still return the finite final answer. This is intentional.
    assert m.metrics([1e-200],[0],[1e-200],[1],[0])['corrected'] == 1
    assert js([case('metrics',[1e-200],[0],[1e-200],[1],[0])])[0]['error'] == 'RangeError'


if __name__ == "__main__":
    suite = unittest.TestSuite(unittest.FunctionTestCase(value) for name, value in list(globals().items()) if name.startswith("test_") and callable(value))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(not result.wasSuccessful())

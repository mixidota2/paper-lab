"""Cross-language independent oracle, algebra, and domain boundary checks."""
import importlib.util
import itertools
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / 'papers/storewide-shelf-decomposition'
spec = importlib.util.spec_from_file_location('shelf_oracle', LAB / 'run.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def js(cases, caps=(1, 2, 3, 4)):
    code = "const m=require(process.argv[1]);let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{let x=JSON.parse(s);console.log(JSON.stringify(x.cases.map(p=>m.solve(p,x.caps))));});"
    return json.loads(subprocess.run(['node', '-e', code, str(LAB/'model.js')], input=json.dumps(dict(cases=cases,caps=caps)), text=True, capture_output=True, check=True).stdout)


def test_default_independent_fixture_and_persisted_results():
    x = m.oracle(m.DEFAULT)
    assert x['profit'] == pytest.approx(150.78059291689343)
    assert x['faces'] == [1, 2, 0, 2, 0, 0]
    assert x['allocation'] == [3, 2]
    assert x['optimal_face_count'] == 1
    stored = json.loads((LAB/'results.json').read_text())
    assert stored['cases'][0]['oracle'] == x
    for case in stored['cases']:
        assert case['oracle'] == m.oracle(case['parameters'])


@pytest.mark.parametrize('caps', [(1,2,3,4),(1,3,4)])
def test_decomposition_matches_729_vector_oracle(caps):
    cases = [dict(m.DEFAULT, s=s, beta=b, r=r, e=e, brands=w, capacity=k)
             for s,b,r,e,w,k in itertools.product((0,.4,1),(0,.25),(0,12),(.5,1),(1,2),(3,5,8))]
    for p, result in zip(cases, js(cases,caps)):
        expected = m.oracle(p,caps)
        actual = result['best']
        if expected is None:
            assert actual is None
            continue
        assert actual['profit'] == pytest.approx(expected['profit'], rel=0, abs=1e-9)
        faces = [f for cat in actual['categories'] for f in cat['faces']]
        assert faces in expected['optimal_face_vectors']
        assert sum(actual['allocation']) <= p['capacity']
        for cat, cap in zip(actual['categories'], actual['allocation']):
            assert cat['used'] <= cap
        for name in ('proportional','ignored'):
            baseline=result[name]
            if baseline and baseline['profit'] is not None:
                assert baseline['profit'] <= actual['profit'] + 1e-9


def test_demand_balance_equation4_and_nonnegative_effective_margin():
    for s,beta,r in itertools.product((0,.4,1),(0,.25,1),(0,4,12)):
        p=dict(m.DEFAULT,s=s,beta=beta,r=r,e=0)
        for start in (0,3):
            items=m.ITEMS[start:start+3]
            for faces in itertools.product(range(3),repeat=3):
                out=m.evaluate(items,faces,p)
                if out is None:
                    assert faces==(0,0,0)
                    continue
                rows=out['rows']
                assert sum(x['transfer'] for x in rows)==pytest.approx(s*out['unmet_base'])
                assert sum(x['demand'] for x in rows)+out['lost']==pytest.approx(sum(x['direct'] for x in rows)+out['unmet_base'])
                assert m.eq4(items,faces,p)==pytest.approx(out['profit'])
                for x,f in zip(items,faces):
                    if f: assert x['p']-r/(f*x['d'])>=0
                if s==0: assert all(x['transfer']==0 for x in rows)
                if all(faces): assert out['unmet_base']==0
                if beta==0: assert sum(x['direct'] for x in rows)==sum(x['q'] for x,f in zip(items,faces) if f)


def test_retention_brands_and_capacity_infeasibility():
    p=dict(m.DEFAULT,e=1)
    assert m.oracle(dict(p,capacity=5)) is None
    assert all(m.oracle(dict(p,capacity=6))['faces'])
    assert m.evaluate(m.ITEMS[:3],(1,1,0),dict(m.DEFAULT,brands=2)) is None
    assert m.oracle(dict(m.DEFAULT,capacity=1)) is None
    results=js([dict(m.DEFAULT,e=1,capacity=5)])
    assert results[0]['best'] is None
    assert results[0]['proportional'] is None


def test_monotonic_capacity_and_candidate_addition():
    values=[m.oracle(dict(m.DEFAULT,capacity=k)) for k in range(2,9)]
    feasible=[x['profit'] for x in values if x]
    assert feasible==sorted(feasible)
    assert m.oracle(m.DEFAULT)['profit']>=m.oracle(m.DEFAULT,(1,3,4))['profit']-1e-9
    table=js([m.DEFAULT])[0]['tables']
    for t in table:
        values=[x['best']['profit'] for x in t if x['best']]
        assert values==sorted(values)


def test_hand_counterexamples_and_printed_equation_fixture():
    xs=[dict(id=str(i),q=10,p=5,w=1,d=1,brand='X') for i in range(2)]
    p=dict(m.DEFAULT,beta=0,s=1,c=2,r=0,e=.5)
    assert m.evaluate(xs,(1,0),p)['profit']==98
    assert m.evaluate(xs,(1,1),p)['profit']==96
    for x in xs: x['p']=1
    p.update(s=.5,c=0)
    assert m.evaluate(xs,(1,0),p)['profit']==15
    assert m.eq4(xs,(1,0),p)==15
    printed_eq2=10*(1-.5)+20
    assert printed_eq2==25
    xs=[dict(id='A',q=20,p=5,w=1,d=2,brand='X'),dict(id='B',q=5,p=4,w=1,d=2,brand='X')]
    p.update(s=0,c=0,r=4)
    assert m.evaluate(xs,(2,0),p)['profit']==80
    assert m.evaluate(xs,(1,1),p)['profit']==70
    p['r']=0
    assert m.evaluate(xs,(2,0),p)['profit']==100
    assert m.evaluate(xs,(1,1),p)['profit']==120


def test_category_permutation_and_money_scaling():
    xs=m.ITEMS[:3]; f=(1,2,0)
    out=m.evaluate(xs,f,m.DEFAULT)
    assert m.evaluate(xs[::-1],f[::-1],m.DEFAULT)['profit']==pytest.approx(out['profit'])
    scaled=[dict(x,p=3*x['p']) for x in xs]
    assert m.evaluate(scaled,f,dict(m.DEFAULT,r=12,c=6))['profit']==pytest.approx(3*out['profit'])


def test_all_ties_and_feasible_proportional_candidates():
    p=dict(m.DEFAULT,capacity=8,s=0,beta=0,r=0,c=0)
    actual=js([p])[0]['best'];expected=m.oracle(p)
    assert actual['profit']==206
    assert actual['optimal_face_count']==16
    assert actual['optimal_face_vectors']==expected['optimal_face_vectors']
    p=dict(m.DEFAULT,e=1,capacity=6)
    proportional=js([p])[0]['proportional']
    assert proportional['allocation']==[3,3]
    assert proportional['feasible']

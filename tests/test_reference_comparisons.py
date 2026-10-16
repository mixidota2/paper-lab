"""Independent expectations for two local teaching models, not paper reproduction."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
IDS = ['reasoncast-agentic-demand-forecasting', 'retailbench-long-horizon-store-agents']

def model(i):
    spec=importlib.util.spec_from_file_location('reference', ROOT/'papers'/IDS[i]/'run.py')
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def reason(**changes):
    m=model(0); x=m.reference_cases()['inputs']; x.update(changes); return m.evaluate(x)

def retail(**changes):
    m=model(1); x=m.reference_cases()['inputs']; x.update(changes); return m.evaluate(x)

@pytest.mark.parametrize('g,expected', [(0,50),(.5,29.28932188134524),(1,0)])
def test_reason_strength_independent_values(g,expected):
    rows=reason(gate=g)['rows']
    assert rows[0]['wmape']==50
    assert rows[1]['wmape']==0
    assert rows[2]['wmape']==pytest.approx(expected,abs=1e-10)
    assert rows[2]['denominator']==140
    assert rows[2]['delta_pp']==pytest.approx(expected-50)

@pytest.mark.parametrize('k,relation', [(.5,'worse'),(1,'tie'),(1.23,'better'),(2,'better'),(2.8,'better'),(3,'tie'),(3.2,'worse')])
def test_reason_multiplier_boundary(k,relation):
    rows=reason(level=[math.log(k)]*7,gate=1)['rows']; diff=rows[2]['delta_pp']
    if relation=='tie': assert diff==pytest.approx(0,abs=1e-12)
    elif relation=='better': assert diff<0
    else: assert diff>0

def test_reason_false_information_and_day_shift():
    assert reason(level=[math.log(.5)]*7,gate=1)['rows'][2]['wmape']==75
    rows=reason(actual=[10]*7,gate=1)['rows'];assert rows[0]['wmape']==0 and rows[2]['wmape']==100
    kw=dict(actual=[10,10,20,10,10,10,10],level=[0]*7,gate=1)
    rows=reason(**kw,additive=[0,0,0,10,0,0,0])['rows']
    assert rows[0]['wmape']==12.5 and rows[2]['wmape']==25
    assert reason(**kw,additive=[0,0,10,0,0,0,0])['rows'][2]['wmape']==0

def test_reason_input_independence_skip_and_missing():
    m=model(0);x=m.reference_cases()['inputs'];original=copy.deepcopy(x)
    a=m.evaluate(x);x['actual']=[13]*7;b=m.evaluate(x)
    assert a['route']==b['route']
    assert [r['prediction'] for r in a['rows']]==[r['prediction'] for r in b['rows']]
    x['level']=[math.log(.5)]*7;m.evaluate(x);assert x['actual']==[13]*7
    x=original;x['route']='Skip';x['base'][0]=-0.0
    result=m.evaluate(x);assert result['rows'][2]['prediction']==x['base']
    assert math.copysign(1,result['rows'][2]['prediction'][0])==-1
    result=reason(actual=[0]*7);assert all(r['wmape'] is None and r['delta_pp'] is None for r in result['rows'])
    assert result['rows'][0]['mae']==10
    result=reason(additive=[-15]*7,gate=1)
    assert result['negative_prediction'] and result['rows'][2]['prediction']==[-10]*7

@pytest.mark.parametrize('field,value',[('base',[1]),('actual',[-1]*7),('actual',[math.nan]*7),('level',[math.inf]*7),('gate',1.1),('gate',-.1),('gate',True),('route','Tool')])
def test_reason_rejects_invalid(field,value):
    with pytest.raises(ValueError): reason(**{field:value})

@pytest.mark.parametrize('rate,cost,expected',[(.05,5,12000),(.2,5,3000),(.25,5,0),(.3,5,-3000),(.05,6.5,3000),(.05,7,0)])
def test_retail_hand_calculated_boundary(rate,cost,expected):
    result=retail(return_b=rate,cost_b=cost)
    assert result['suppliers'][0]['final_cash']==pytest.approx(3000)
    assert result['suppliers'][1]['final_cash']==pytest.approx(expected)


def test_retail_cash_constraint_reverses_margin_rank_and_stops():
    kw=dict(mode='funded',cash=40,demand=10,price=10,rent=35,days=2,return_a=.15,return_b=0)
    result=retail(**kw);a,b=result['suppliers']
    assert a['margin']==4.5<b['margin']==5
    assert [t['cash'] for t in a['trace']]==[50,60]
    assert [t['cash'] for t in b['trace']]==[45,55]
    assert [t['sold'] for t in b['trace']]==[8,9]
    kw.update(rent=80,days=4);a=retail(**kw)['suppliers'][0]
    assert a['stopped']==2
    assert [t['cash'] for t in a['trace']]==[5,-70.5,-70.5,-70.5]
    assert all(t[k]==0 for t in a['trace'][2:] for k in ('purchase','gross','refund','rent','sold','lost'))

@pytest.mark.parametrize('mode',['accounting','funded'])
def test_retail_identity_same_supplier_and_missing(mode):
    result=retail(mode=mode,cost_b=4,return_b=.3)
    a,b=result['suppliers'];assert a['trace']==b['trace']
    for t in a['trace']:
        assert t['cash']==pytest.approx(t['opening']-t['purchase']+t['gross']-t['refund']-t['rent'])
        if mode=='funded':assert t['purchase']<=max(0,t['opening'])
    r=retail(mode=mode,demand=0,price=0)
    assert r['return_b_tie'] is None
    assert all(t['return_ratio'] is None for s in r['suppliers'] for t in s['trace'])

@pytest.mark.parametrize('field,value',[('return_b',1.1),('cost_a',-1),('demand',math.nan),('days',0),('days',1.5),('cash',-1),('price',math.inf),('mode','unknown')])
def test_retail_rejects_invalid(field,value):
    with pytest.raises(ValueError): retail(**{field:value})

@pytest.mark.parametrize('changes',[dict(cost_a=0),dict(demand=1.5)])
def test_funded_requires_positive_cost_integer_demand(changes):
    with pytest.raises(ValueError):retail(mode='funded',**changes)

@pytest.mark.parametrize('i',[0,1])
def test_saved_reference_and_cli_recompute(i,tmp_path):
    m=model(i);source=ROOT/'papers'/IDS[i]
    saved=json.loads((source/'results.json').read_text())
    assert saved['reference']==m.reference_cases()
    shutil.copy2(source/'run.py',tmp_path/'run.py')
    subprocess.run([sys.executable,str(tmp_path/'run.py')],check=True,capture_output=True)
    assert json.loads((tmp_path/'results.json').read_text())==saved
    payload=tmp_path/'comparison.json';payload.write_text(json.dumps({**m.pack(saved['reference']['inputs']), 'output':'untrusted'}))
    run=subprocess.run([sys.executable,str(tmp_path/'run.py'),'--input',str(payload)],check=True,capture_output=True,text=True)
    assert json.loads(run.stdout)==saved['reference']['output']


def test_finite_inputs_cannot_export_nonfinite_metrics():
    assert reason(base=[1e200]*7,actual=[1e-200]*7)['rows'][0]['status']=='unavailable'
    with pytest.raises(ValueError):retail(price=1e-320,demand=0)
    result=retail(mode='funded',cash=1,demand=1,cost_a=5e-324,cost_b=5e-324,days=1)
    assert result['suppliers'][0]['trace'][0]['sold']==1

@pytest.mark.parametrize('cash,expected',[(.3,3),(.29999999999999993,2),(.30000000000000004,3),(.299,2)])
def test_decimal_budget_has_no_affordability_epsilon(cash,expected):
    result=retail(mode='funded',cash=cash,cost_a=.1,cost_b=.1,demand=3,price=0,rent=0,days=2,return_a=0,return_b=0)
    a=result['suppliers'][0]
    assert a['trace'][0]['sold']==expected
    assert a['trace'][0]['purchase']<=cash
    assert a['trace'][0]['cash']>=0
    assert a['stopped'] is None
    if cash==.3:
        assert a['trace'][0]['purchase']==.3
        assert a['trace'][0]['cash']==0
        assert a['trace'][1]['sold']==0


def test_decimal_cash_is_carried_without_binary_drift():
    a=retail(mode='funded',cash=.3,cost_a=.1,cost_b=.1,demand=3,price=.1,rent=0,days=30,return_a=0,return_b=0)['suppliers'][0]
    assert all(t['sold']==3 and t['cash']==.3 for t in a['trace'])


def test_skip_survives_nonselected_overflow_and_warns_negative_baseline():
    r=reason(route='Skip',level=[1000]*7)
    assert r['rows'][1]['status']=='unavailable'
    assert r['rows'][1]['prediction'] is None
    assert r['rows'][2]['status']=='ok'
    assert r['rows'][2]['prediction']==[10]*7
    assert r['rows'][2]['wmape']==50
    r=reason(route='Correct',gate=.001,level=[1000]*7)
    assert r['rows'][1]['status']=='unavailable' and r['rows'][2]['status']=='ok'
    r=reason(base=[-10]*7,additive=[20]*7,level=[0]*7,gate=1)
    assert r['negative_prediction'] and r['rows'][2]['prediction']==[10]*7

@pytest.mark.parametrize('i',[0,1])
def test_saved_model_contract(i):
    m=model(i);x=m.reference_cases()['inputs'];packet=m.pack(x)
    assert packet['schema']==2
    assert packet['model']['source']['url'].startswith('https://arxiv.org/html/')
    assert packet['model']['conventions']
    packet['output']='forged';assert m.unpack(packet)==x
    packet['model']={**packet['model'],'version':'unknown'}
    with pytest.raises(ValueError):m.unpack(packet)

@pytest.mark.parametrize('demand', [0, 1, 9007199254740990, 9007199254740991])
def test_funded_safe_integer_boundary(demand):
    result = retail(mode='funded', demand=demand, cash=1e20, cost_a=1, cost_b=1,
                    price=0, rent=0, return_a=0, return_b=0, days=1)
    for supplier in result['suppliers']:
        assert supplier['trace'][0]['sold'] == demand
        assert supplier['trace'][0]['lost'] == 0

@pytest.mark.parametrize('demand', [9007199254740992, 1000000000000000100, -1, .5])
def test_funded_rejects_unsafe_demand(demand):
    with pytest.raises(ValueError):
        retail(mode='funded', demand=demand)

def test_reason_large_finite_predictions():
    result = reason(base=[1e307]*7, actual=[1e307]*7, additive=[0]*7, level=[0]*7)
    assert all(row['status']=='ok' and row['wmape']==0 for row in result['rows'])

@pytest.mark.parametrize('i', [0, 1])
def test_python_export_identifies_actual_source(i):
    import hashlib
    m = model(i)
    packet = m.pack(m.reference_cases()['inputs'])
    assert packet['implementation'] == {
        'status': 'content-hash', 'algorithm': 'sha256', 'runtime': 'python',
        'files': {'run.py': hashlib.sha256((ROOT/'papers'/IDS[i]/'run.py').read_bytes()).hexdigest()}}
    packet['implementation'] = {'status': 'untrusted-old-implementation'}
    assert m.pack(m.unpack(packet))['implementation']['status'] == 'content-hash'

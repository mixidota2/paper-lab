"""Boundary and provenance checks for September 18 explanatory experiments."""
import importlib.util
import json
from pathlib import Path
import pytest
import yaml

ROOT=Path(__file__).resolve().parents[1]
SLUGS=['ogr-once-generated-ranked','dream-taobao-agentic-control','pilot-experiment-lifecycle']

def module(i):
    spec=importlib.util.spec_from_file_location(SLUGS[i],ROOT/'papers'/SLUGS[i]/'run.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m

@pytest.mark.parametrize('i',range(3))
def test_reproducibility_and_source_contract(i):
    path=ROOT/'papers'/SLUGS[i]
    assert json.loads(json.dumps(module(i).compute()))==json.loads((path/'results.json').read_text())
    y=yaml.safe_load((path/'lab.yaml').read_text())
    assert len(y['source_review']['pdf_sha256'])==64
    assert y['source_review']['pdf_sha256'] in (path/'mapping.md').read_text()
    assert y['source_review']['version'] in y['urls']['pdf']
    assert y['verification']['performance']=='NOT TESTED'
    assert all(y['sections'].get(k) for k in ['overview','problem','method','evidence','why_it_might_work','executable_understanding','what_we_verified','what_we_did_not_verify','implementation','mapping'])

def test_ogr_dependency_depth_and_non_speedup_boundary():
    m=module(0)
    x=m.schedule(5,4)
    assert x['pipeline']==9 and x['serial']==20 and x['total_operations']==25
    assert m.schedule(1,4)['ratio']<1
    for k in [1,2,5,20]:
        for d in [1,2,4]:
            x=m.schedule(k,d)
            assert x['pipeline']==k+d
            assert all(b==a+1 for lane in x['lanes'] for a,b in zip(lane,lane[1:]))
    with pytest.raises(ValueError):m.schedule(0,4)

def test_ogr_shared_hash_distinct_support_and_cold_start():
    m=module(0)
    a,ua=m.sketch({'u':['A','B']})
    b,ub=m.sketch({'u':['A','B','A','B']})
    assert ua['A']==ub['A']==1 and a['A']!=b['A']
    assert m.confidence(0)==0
    assert m.confidence(1)<m.confidence(100)<.35
    assert m.fuse([3,4],[4,3],0)==[.6,.8,0,0]
    for n in [0,1,10]:assert sum(x*x for x in m.fuse([3,4],[4,3],m.confidence(n)))==pytest.approx(1)

def test_spa_primary_direction_even_when_naive_sum_reverses():
    m=module(0)
    assert m.calibrate(1,-2)['naive_sum']<0
    assert m.calibrate(1,-2)['calibrated']==1
    assert m.standardize([3,3,3])==[0,0,0]
    for p in [-3,-1,0,1,3]:
        for a in [-10,-1,0,1,10]:
            x=m.calibrate(p,a)['calibrated']
            assert (x>0)-(x<0)==(p>0)-(p<0)

def test_dream_local_override_and_fail_closed():
    m=module(1); original=dict(m.DEFAULT)
    valid={'version':1,'expires':120,'boost':{'ipv':2},'category':-2}
    x,status=m.compile_strategy(valid)
    assert status=='override' and x['ipv']==1.4 and x['scatter']==1
    assert x['ctr']==m.DEFAULT['ctr'] and m.DEFAULT==original
    for b in [None,{},dict(valid,version=True),dict(valid,expires=100),dict(valid,expires=float('nan')),dict(valid,boost={'ipv':True}),dict(valid,boost={'ipv':3}),dict(valid,boost={'unknown':1}),dict(valid,global_write=True)]:
        x,status=m.compile_strategy(b)
        assert x==original and status.startswith('fallback')
    assert m.invoke(.7,.7,1) and not m.invoke(.9,.7,0)
    assert m.replay_reward([1,1],[1,1])==0
    assert m.replay_reward([1,1],[1,1.2])==1

def test_pilot_permission_and_independent_confirmation():
    m=module(2)
    assert m.transition('frozen','launch')=='frozen'
    assert m.transition('frozen','launch',approved=True)=='observe'
    assert m.transition('observe','promote',healthy=False)=='paused'
    assert m.transition('confirm','deliver',approved=True)=='confirm'
    assert m.transition('confirm','deliver',approved=True,confirm=True)=='delivered'
    assert m.transition('delivered','launch',approved=True)=='delivered'
    assert m.memory([('A','positive')]*10)['state']=='draft'
    assert m.memory([('A','positive'),('B','positive')])['state']=='supported'
    assert m.memory([('A','positive'),('B','inconclusive')])['conflict'] is False
    assert m.memory([('A','positive'),('B','negative')])['conflict'] is True
    assert m.route({},True)=='default_bundle'
    assert not m.admissible([])
    assert not m.admissible([{'segment':'focused'}]*9+[{}])

@pytest.mark.parametrize('supports,state',[(1,'draft'),(2,'supported'),(3,'approved')])
def test_memory_contradiction_retains_state_and_blocks_later_promotion(supports,state):
    m=module(2)
    prior=[(str(i),'positive') for i in range(supports)]
    for later in [[], [('later','positive')]*5+[('another','positive')]]:
        evidence=prior+[('opposing','negative')]+later+[('neutral','inconclusive')]
        result=m.memory(iter(evidence))
        assert result['state']==state
        assert result['conflict'] is True
        assert result['observations']==evidence
        assert result['sources']==supports+(2 if later else 0)
    assert m.memory(prior+[('neutral','inconclusive')])['state']==state
    assert m.memory(prior*10)['state']==state

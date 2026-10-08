"""Mechanism checks, independent of the paper's empirical performance."""
import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]

def module(slug):
    spec=importlib.util.spec_from_file_location(slug,ROOT/'papers'/slug/'run.py')
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_exact_mcnemar_limits_and_direction_symmetry():
    m=module('harness-buys-tokens-not-pass-rate')
    assert m.rejection(5)==-1
    assert m.rejection(6)==0
    assert m.power(45,.14,0)<=.05
    assert m.power(447,.14,0)<=.05
    assert m.mde(45,.14,.8) is None
    assert m.mde(45,.14,.5)==pytest.approx(12.9,abs=.02)
    assert m.power(447,.14,.06)>m.power(447,.14,.03)


def test_oracle_can_be_useless_even_with_multiple_actions():
    m=module('traffic-forecast-to-decision-value')
    a=m.experiment([0,1,2]);b=m.experiment([4,8,12])
    assert a['improved']['mae']==b['improved']['mae']
    assert a['oracle']['decision_loss']==a['historical']['decision_loss']
    assert b['oracle']['decision_loss']<b['historical']['decision_loss']


def test_guard_protects_old_requests_without_claiming_deadline():
    m=module('hear-harness-engine-serving-protocol')
    plain=m.schedule('cache');guard=m.schedule('cache_guard');fcfs=m.schedule('fcfs')
    assert plain['mean_ttft']<fcfs['mean_ttft']
    assert plain['max_ttft']>fcfs['max_ttft']
    assert guard['max_ttft']<plain['max_ttft']
    assert guard['max_ttft']>8
    for c in [plain,guard,fcfs]:
        assert sorted(t['id'] for t in c['trace'])==sorted(t['id'] for t in plain['trace'])
        assert all(a['end']<=b['start'] for a,b in zip(c['trace'],c['trace'][1:]))


def test_inventory_conservation_and_calibration_never_reads_future():
    np=pytest.importorskip('numpy')
    m=module('sim2real-policy-conditioned-inbound-forecast')
    a=m.rollout(23,'new',cost=0,weeks=40)[2]
    b=m.rollout(23,'new',cost=4,weeks=40)[2]
    assert [r['demand'] for r in a]==[r['demand'] for r in b]
    assert [r['orders'] for r in a]!=[r['orders'] for r in b]
    for r in a+b:
        assert r['inventory']==pytest.approx(r['before']+r['inbound']-r['sales'])
        assert r['inventory']>=0
    pred=np.arange(1.,21.)
    truth=pred*1.2+4
    altered=truth.copy();altered[10:]+=1000
    assert np.allclose(m.calibrate(pred,truth)[:7],m.calibrate(pred,altered)[:7])

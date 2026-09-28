"""Reproducibility and boundary tests for the September 28 teaching mechanisms."""
import importlib.util
import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
SLUGS=['reasoncast-agentic-demand-forecasting','scope-coupled-supply-chain-policies','onetrans-v2-cascade-unification','evaluation-choices-forecasting-leaderboard','harness-zero-distillation']
def module(i):
    spec=importlib.util.spec_from_file_location('toy',ROOT/'papers'/SLUGS[i]/'run.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
@pytest.mark.parametrize('slug',SLUGS)
def test_standalone_reproduction(slug,tmp_path):
    src=ROOT/'papers'/slug
    shutil.copy(src/'run.py',tmp_path/'run.py')
    subprocess.run([sys.executable,str(tmp_path/'run.py')],check=True,capture_output=True)
    assert json.loads((tmp_path/'results.json').read_text())==json.loads((src/'results.json').read_text())
def test_skip_bypasses_invalid_semantics_bit_exactly():
    m=module(0);b=[-0.0,.1,1e100]
    actual=m.correct(b,'Skip',[float('nan')]*3,[float('inf')]*3)
    assert b is not actual
    assert b''.join(struct.pack('d',v) for v in b)==b''.join(struct.pack('d',v) for v in actual)
    assert m.wmape([0],[0]) is None
    assert m.correct(b,'Basic',[0]*3,[0]*3)==b

def test_capacity_threshold_and_cost_change_decision():
    m=module(1)
    assert m.utility('B',2,10)['vehicles']==1
    assert m.utility('B',3,10)['vehicles']==2
    f=m.experiment()['frames']
    assert f[0]['proposed']['item']=='A'
    assert f[-1]['proposed']['item']=='B'
    assert all(x['proposed']['utility']>=x['baseline']['utility'] for x in f)

def test_dcgr_recovers_probability_ranking_and_steers():
    m=module(2)
    assert [x['item'] for x in m.rank(0)]==['A','B','C']
    assert [m.rank(b)[0]['item'] for b in [0,1,2]]==['A','B','C']

def test_aggregation_flip_uses_identical_predictions():
    m=module(3);r=m.experiment()
    assert [f['winner'] for f in r['frames']]==['A','A','B','B']
    assert r['frames'][0]['scores']['A']==0
    assert r['frames'][-1]['scores']['A']==40
    assert all(f['scores']['B']==10 for f in r['frames'])

def test_rejected_action_cannot_become_training_target():
    m=module(4)
    assert m.collect('bad','REPLACE','good')['training_targets']==['good']
    assert m.collect('good','PASS')['executed']=='good'
    with pytest.raises(ValueError):m.collect('bad','REPLACE')
    with pytest.raises(ValueError):m.collect('bad','unknown')

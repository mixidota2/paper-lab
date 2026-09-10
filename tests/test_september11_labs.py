"""Boundary checks for the September 11 illustrative mechanisms."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'papers'/name/'run.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_dc_learns_even_a_reversed_teacher_without_creating_candidates():
    m = load('oneranker-ads')
    for teacher in ([3.,1.,.5,0.], [-1.,0.,1.,2.]):
        frames = m.align(teacher=teacher)
        assert frames[-1]['kl_teacher_generator'] < frames[0]['kl_teacher_generator']
        assert frames[-1]['top2_disagreement'] == 0
        assert len(frames[-1]['generator']) == 4


def test_refresh_does_not_guarantee_fewer_collisions():
    m = load('tagr-live-sid')
    for xs in ([.05,1.05,2.05,3.05], [.05]*4):
        r = m.scenario(xs)
        for mode in ('static', 'refreshed'):
            assert r[mode]['cpr'] >= 1+r[mode]['col']
        assert r['refreshed']['semantic_mse'] <= r['static']['semantic_mse']
    r = m.scenario([.05]*4)
    assert r['refreshed']['cpr'] > r['static']['cpr']


def test_missing_evidence_and_completed_repairs_prevent_intervention():
    m = load('agenttether-repair')
    assert m.localize({0:[],1:[0],2:[]}, 2, [0,1]) is None
    assert not m.guard(10,0,False,True)
    assert not m.guard(10,0,True,True,complete=True)
    assert not m.guard(10,9,True,True)
    assert not m.guard(10,0,True,True,after_write=True)
    assert m.guard(10,0,True,True,after_write=True,loop=True)
    result = m.experiment()['localization']
    assert result['dependency'] == result['true_root']
    assert result['missing_edge_counterexample'] != result['true_root']

"""Mechanism boundaries for September 10 synthetic experiments."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'papers'/name/'run.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_rescoring_is_bounded_by_reachable_candidates():
    m = module('gryphon-ilsm')
    for k in (1, 2, 3):
        for reverse in (False, True):
            r = m.experiment(k, reverse)
            assert set(r['beam_order']) == set(r['item_order']) == set(r['pool'])
            assert r['item_recall@2'] <= r['reachable_recall_ceiling']
    assert m.experiment(3)['item_recall@2'] == 1
    assert m.experiment(2)['item_recall@2'] < 1


def test_mae_source_normalization_and_missing_feature_support():
    m = module('gryphon-v2-cascade')
    a, b = [(-1., 0.), (1., 0.)], [(0., -1.), (0., 1.)]
    assert m.fit([a])[1] == 0
    assert m.fit([b])[0] == 0
    base = m.fit([a, b])
    repeated = m.fit([a*3, b])
    assert all(abs(x-y)<.01 for x, y in zip(base, repeated))
    assert m.evaluate(base, [(.7, .8), (-.7, -.8)])['teacher_mae'] < .01


def test_selective_recovery_matches_fresh_execution_for_all_revisions():
    from itertools import combinations
    m = module('revise-recovery')
    for n in range(4):
        for keys in combinations(['budget', 'city', 'style'], n):
            for mode in ('complete', 'unknown'):
                r = m.experiment(list(keys), mode)
                assert all(p['oracle_equal'] for p in r['policies'].values())
                assert r['policies']['selective']['calls'] <= r['policies']['restart']['calls']
    assert not m.commit_valid(['plan.budget'], [['plan']])
    assert m.commit_valid(['plan.city'], [['plan.budget']])
    assert not m.commit_valid([], [], parents_current=False)
    assert not m.commit_valid([], [], complete=False)
    assert not m.commit_valid([], [], effect_safe=False)

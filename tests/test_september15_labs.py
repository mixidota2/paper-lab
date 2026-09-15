"""Information boundaries, numerical invariants and reproducible batch artifacts."""
import importlib.util
import json
import math
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ('oxygenrec-v2-idgr', 'recevolve-autonomous-rec', 'quasid-collision-qualified-sid')


def module(slug):
    spec = importlib.util.spec_from_file_location(slug, ROOT / 'papers' / slug / 'run.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize('slug', SLUGS)
def test_saved_results_are_reproducible(slug):
    assert module(slug).compute() == json.loads((ROOT / 'papers' / slug / 'results.json').read_text())
    for filename in ('README.md', 'lab.yaml', 'mapping.md', 'method.md'):
        assert (ROOT / 'papers' / slug / filename).stat().st_size > 100


def test_oxygen_reward_gates_and_empty_routes():
    toy = module(SLUGS[0])
    assert toy.reward([1, 2, 3], [1, 2, 3]) == pytest.approx(1)
    assert toy.reward([1, 2, 3], [4, 5, 6]) == 0
    assert toy.reward([1, 9, 9], [1, 2, 3], gamma=1) == pytest.approx(1 / 3)
    p = [.5, .5]
    h = toy.entropy(p)
    assert toy.gates(p, h, h) == {'entropy': h, 'low': 0, 'high': 0}
    terms = toy.losses([p], [p], [0], [0], low=0, high=10)
    assert terms['SD'] == terms['FKL'] == 0
    assert math.isfinite(terms['weighted_without_SFT'])
    routes = toy.compute()['loss_terms']['routes']
    assert [(r['low'], r['high']) for r in routes] == [(1, 0), (0, 0), (0, 1)]
    pooled = toy.instruction_probe(conditioned=False)
    assert pooled[0] == pooled[1] == pooled[2]
    assert len({tuple(p) for p in toy.instruction_probe()}) == 3


def test_fixed_scores_cannot_improve_when_negatives_are_added():
    toy = module(SLUGS[1])
    previous = None
    for n in (0, 1, 5, 100):
        result = toy.score_query(0, [1] * n)
        assert result['rank'] == n + 1
        if previous is not None:
            assert result['ndcg'] <= previous
        previous = result['ndcg']
    for seed in (15, 16):
        values = list(toy.candidate_probe(seed, queries=16).values())
        assert values == sorted(values, reverse=True)


def test_rollback_preserves_snapshot_and_keep_requires_auxiliary_guard():
    toy = module(SLUGS[1])
    trace = toy.lifecycle()
    assert [r['status'] for r in trace] == ['ROLLBACK'] * 4 + ['KEEP']
    for row in trace[:4]:
        assert row['before'] == row['after']
    assert toy.lifecycle(False)[2]['status'] == 'KEEP'
    assert trace[-1]['after']['candidates'] == 8000


def test_quasid_excludes_benign_pairs_and_normalizes_groups():
    toy = module(SLUGS[2])
    ids = ['a', 'a', 'c', 'b', 'd', 'e']
    assert not toy.qualified(0, 1, ids, 3)
    assert not toy.qualified(0, 3, ids, 3)
    assert not toy.qualified(3, 0, ids, 3)
    assert toy.qualified(0, 2, ids, 3)
    assert toy.pair_loss(2, 0, radius=1) == 0
    assert toy.pair_loss(2, 0, radius=2) == .5
    assert toy.pair_loss(0, .8) == toy.pair_loss(1, .5) == 0
    empty = toy.hamr(['a', 'a'], [(1,), (1,)], [0, 0], 1)
    assert empty['loss'] == 0
    data = toy.compute()['masked']
    expected = 0
    for hgroup, weight in [('full', .2), ('partial', .1)]:
        pairs = [p for p in data['pairs'] if p['qualified'] and
                 (p['hamming'] == 0 if hgroup == 'full' else 0 < p['hamming'] <= 2)]
        expected += weight * 2 * sum(p['loss'] for p in pairs) / (2 * len(pairs) + 1e-8)
    assert data['loss'] == pytest.approx(expected)
    trace = toy.angular_update()
    assert trace[-1]['distance'] >= .8
    assert trace[-1]['loss'] == 0
    assert toy.compute()['checks']['discrete_collision_reduction_in_fixed_SIDs'] == 'NOT OBSERVED'

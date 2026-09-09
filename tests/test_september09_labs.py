"""Mechanism invariants for the six featured 2026-09-09 papers."""
import importlib.util
import json
import math
from pathlib import Path
from xml.etree import ElementTree

import pytest

ROOT = Path(__file__).resolve().parents[1]
IDS = ('otto-gbdt-vs-dnn-ltr', 'multi-harness-rl', 'autolr-dashen',
       'sid-ope-hierarchy', 'walmart-demand-transfer', 'harness-r1')


def module(slug):
    spec = importlib.util.spec_from_file_location(slug, ROOT / 'papers' / slug / 'run.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize('slug', IDS)
def test_results_are_reproducible_and_do_not_claim_paper_performance(slug):
    expected = json.loads((ROOT / 'papers' / slug / 'results.json').read_text())
    assert module(slug).compute() == expected
    assert expected['verification']['production_applicability'] == 'NOT TESTED'
    assert expected['verification']['performance'] == 'NOT TESTED'


def test_ltr_targets_have_orders_contained_in_clicks_and_ndcg_is_rank_sensitive():
    toy = module(IDS[0])
    for _, click, order in toy.dataset(17, 30):
        assert sum(click) > 0 and sum(order) > 0
        assert all(o <= c for o, c in zip(order, click))
    assert toy.ndcg([3, 2, 1], [1, 0, 0]) == 1
    assert toy.ndcg([1, 2, 3], [1, 0, 0]) < 1
    # Constant shifts do not change softmax or ranks.
    assert toy.softmax([1, 2, 3]) == pytest.approx(toy.softmax([101, 102, 103]))


def test_grouping_creates_signal_without_changing_frozen_rewards():
    toy = module(IDS[1])
    assert toy.advantages([1, 1, 1]) == [0, 0, 0]
    mixed = toy.advantages([1, 1, 0])
    assert sum(mixed) == pytest.approx(0)
    assert mixed[0] > 0 > mixed[-1]
    result = toy.experiment()
    a_rows = [r for r in result['trajectories'] if r['harness'] == 'A']
    assert all(r['within'] == 0 and r['cross'] > 0 for r in a_rows)
    assert result['held_out_before'] == result['held_out_after_credit_only']


def test_keep_changes_lineage_only_when_accepted_but_never_true_value():
    toy = module(IDS[2])
    for gated in (False, True):
        result = toy.simulate(9, gated)
        previous = 0
        score = 0
        for step in result['path']:
            assert step['parent'] == previous
            assert (step['trunk'] != previous) == step['keep']
            assert step['reported_cumulative_gain'] >= score
            assert step['true_gain'] == 0
            previous, score = step['trunk'], step['reported_cumulative_gain']
    assert toy.simulate(9, True)['keeps'] < toy.simulate(9, False)['keeps']


def test_prefix_mass_and_exact_item_ips_expectation():
    toy = module(IDS[3])
    p0, pe, reward = toy.policies()
    assert sum(p0) == pytest.approx(1)
    assert sum(pe) == pytest.approx(1)
    assert all(p > 0 for p in p0)
    truth = sum(p*r for p, r in zip(pe, reward))
    item_expectation = sum(p0[a]*pe[a]/p0[a]*reward[a] for a in range(64))
    assert item_expectation == pytest.approx(truth)
    for policy in [p0, pe]:
        for depth in range(4):
            masses = toy.cluster_masses(policy, depth)
            assert sum(masses) == pytest.approx(1)
            for c, mass in enumerate(masses):
                assert toy.decoder_prefix(policy, c, depth) == pytest.approx(mass)


def test_demand_conservation_outside_support_and_complete_loyalty():
    toy = module(IDS[4])
    r = toy.experiment()
    assert sum(r['demand']) == pytest.approx(sum(r['adjusted']) + r['lost_demand'])
    assert r['adjusted'][3] == r['demand'][3]
    assert all(r['coefficients'][i][i] == 0 for i in range(4))
    dt = toy.coefficients([0, math.log(3), 0], [{1, 2}, {0, 2}, {0, 1}], [1, 1, 1])
    assert all(sum(row) == 0 for row in dt)
    values, lost = toy.remove_one([100, 60, 40], dt, 0)
    assert values == [0, 60, 40] and lost == 100


def test_runtime_patches_preserve_success_and_unseen_faults_are_not_repaired():
    toy = module(IDS[5])
    data = toy.tasks(0)
    failures = [(t, toy.run_task(t, set())[1]) for t in data if not toy.run_task(t, set())[0]]
    patch = toy.engineer(failures)
    assert patch == set(toy.HOOKS)
    for t in data:
        assert toy.run_task(t, patch)[0] >= toy.run_task(t, set())[0]
    for hook in toy.HOOKS:
        assert toy.evaluate(toy.tasks(100), patch-{hook}) < toy.evaluate(toy.tasks(100), patch)
    # Unknown errors do not magically map to an allowed hook.
    assert toy.engineer([(None, [{'response': {'error': 'unknown'}}])]) == set()


@pytest.mark.parametrize('slug', IDS)
def test_figures_have_accessible_descriptions(slug):
    figures = list((ROOT / 'papers' / slug / 'figures').glob('*.svg'))
    assert len(figures) >= 2
    for figure in figures:
        root = ElementTree.parse(figure).getroot()
        assert root.attrib['viewBox']
        assert root.find('{http://www.w3.org/2000/svg}title').text
        assert root.find('{http://www.w3.org/2000/svg}desc').text

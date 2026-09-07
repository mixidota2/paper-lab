"""Verify honest numerical boundaries and generated UI data contracts."""
import importlib.util
import json
from pathlib import Path

import pytest
import yaml

from paper_lab.models import LabError, lab_from_dict, load_all_labs

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('teaching', ROOT / 'papers/_toy_common.py')
toy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toy)


@pytest.mark.parametrize('lab_id', toy.IDS)
def test_checked_in_results_are_computed_and_reproducible(lab_id):
    actual = json.loads((ROOT / 'papers' / lab_id / 'results.json').read_text())
    assert actual == toy.compute(lab_id)
    assert actual['verification']['performance'] == 'NOT TESTED'


def test_retry_completion_and_cost_are_monotone():
    done = [toy.scaffold(n)['bars'][1]['value'] for n in range(5)]
    assert done == [15, 30, 45, 60, 60]


def test_full_search_recovers_best_leaf_but_greedy_can_lose_it():
    assert toy.retrieval(1)['bars'][1]['value'] < .99
    assert toy.retrieval(4)['bars'][1]['value'] == .99


def test_cache_saves_nothing_for_empty_history():
    empty = toy.cache(0)['bars']
    assert empty[0]['value'] == empty[1]['value']
    nonempty = toy.cache(16)['bars']
    assert nonempty[0]['value'] > nonempty[1]['value']


def test_bad_calendar_can_be_worse_than_ignoring_calendar():
    assert toy.apollo(0)['bars'][1]['value'] == 0
    assert toy.apollo(4)['bars'][1]['value'] > toy.apollo(4)['bars'][0]['value']


def test_stockout_mask_does_not_claim_to_recover_demand():
    assert '推定不能' in toy.stockout(12)['note']
    assert toy.stockout(20)['bars'][2]['value'] < toy.stockout(20)['bars'][0]['value']
    assert len({b['value'] for b in toy.stockout(25)['bars']}) == 1


def test_inventory_cost_order_reverses():
    cheap = toy.cost(.1)['bars']; expensive = toy.cost(2)['bars']
    assert cheap[0]['value'] < cheap[1]['value']
    assert expensive[0]['value'] > expensive[1]['value']


def test_fixing_artifact_format_does_not_fix_missing_evidence():
    assert toy.harness(2)['bars'][1]['value'] == 48 < 60


def test_critic_extreme_thresholds_show_tradeoff():
    assert toy.critic(0)['bars'][1]['value'] == 100
    assert toy.critic(10)['bars'][1]['value'] == 0


def test_all_labs_have_two_valid_interactives_and_sources():
    labs = load_all_labs(ROOT / 'papers')
    for lab in labs:
        assert [s['kind'] for s in lab.interactives] == ['flow','explorer']
        assert lab.question and lab.source_review['url'].startswith('https://')
        assert '一次資料' in lab.sections['evidence']


@pytest.mark.parametrize('bad', ['missing_results', 'nan', 'default', 'stage', 'kind'])
def test_invalid_interactive_data_fails_build(tmp_path, bad):
    source = ROOT / 'papers/unipinrec'
    raw = yaml.safe_load((source / 'lab.yaml').read_text())
    raw['figures'] = []
    result = json.loads((source / 'results.json').read_text())
    if bad == 'missing_results': result = {}
    if bad == 'nan': result['explorer']['frames'][0]['bars'][0]['value'] = float('nan')
    if bad == 'default': result['explorer']['default'] = 999
    if bad == 'stage': del raw['interactives'][0]['stages'][0]['detail']
    if bad == 'kind': raw['interactives'][0]['kind'] = 'unknown'
    (tmp_path / 'results.json').write_text(json.dumps(result))
    with pytest.raises(LabError): lab_from_dict(raw, tmp_path)

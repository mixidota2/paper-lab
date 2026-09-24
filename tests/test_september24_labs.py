"""Reproducibility and evidence boundaries for the September 24 batch."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ['spotify-incremental-recommendation-causal', 'pinterest-causal-retrieval-shopping',
         'swe-serve-inference-serving-agents', 'sam-d2q-aliexpress-doc2query',
         'igpo-huawei-inventory-grounded-search']


def module(slug):
    spec = importlib.util.spec_from_file_location(slug, ROOT/'papers'/slug/'run.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.mark.parametrize('slug', SLUGS)
def test_standalone_results_match_sources(slug, tmp_path):
    src = ROOT/'papers'/slug
    shutil.copy2(src/'run.py', tmp_path/'run.py')
    subprocess.run([sys.executable, str(tmp_path/'run.py')], check=True)
    assert json.loads((tmp_path/'results.json').read_text()) == json.loads((src/'results.json').read_text())
    y = yaml.safe_load((src/'lab.yaml').read_text())
    assert y['source_review']['pdf_sha256'] in (src/'mapping.md').read_text()
    assert all(y['verification'][k] == 'NOT TESTED' for k in ['performance','scaling','production_applicability'])


def test_inventory_probe_cannot_establish_absence():
    m = module(SLUGS[-1])
    hidden = m.search('wedding', m.BASE, True, ['a','b'])
    assert hidden['id'] is None and hidden['decision'] == 'no_support_observed'
    assert m.evaluate(m.BASE, True, ['a','b'])['fni_pct'] == pytest.approx(100/3)
    assert m.search('wedding', m.BASE, True)['id'] == 'c'
    assert m.portrait([])['fill_rates'] == {'tags': 0, 'description': 0}
    assert m.search('photo', [], True)['id'] is None


def test_inventory_replay_blocks_background_regression():
    m = module(SLUGS[-1])
    assert not m.replay_gate([0,1], [1,0], [0], [1])
    assert m.replay_gate([0,1], [1,1], [0], [1])
    assert not m.replay_gate([0,1], [0,1], [0], [1])


def test_verifier_exposes_wiring_and_state_bugs():
    m = module(SLUGS[2])
    assert m.checks('local-only') == dict(local=True, api=False, state=False)
    assert m.checks('state-leak') == dict(local=True, api=True, state=False)
    assert not any(m.checks('no-op').values())
    assert all(m.checks('complete').values())


def test_expansion_gating_removes_false_match_without_losing_recall():
    m = module(SLUGS[3])
    full, gated = m.evaluate('all'), m.evaluate('gated')
    assert gated['true_positive'] == full['true_positive'] == 3
    assert gated['false_positive'] == 0 < full['false_positive']
    assert m.retrieve({'a': {'red','shirt'}}, 'red bag') == set()


def test_dual_threshold_monotonicity_and_mismatched_window_counterexample():
    m = module(SLUGS[0])
    assert m.evaluate(.14)['selected'] == []
    assert m.evaluate(.15)['selected'] == ['persuadable']
    assert m.evaluate(1)['impressions'] == 3
    counts = [m.evaluate(t/100)['impressions'] for t in range(101)]
    assert counts == sorted(counts)
    organic = m.ROWS[0]
    assert organic['p1_short']-organic['p0_long'] < 0 < organic['y1']-organic['y0']


def test_balanced_holdout_dr_correction_and_replay():
    m = module(SLUGS[1])
    for name, p1, p0 in m.TYPES:
        rows = [r for r in m.rows if r['name'] == name]
        assert sum(m.dr(r) for r in rows)/len(rows) == pytest.approx(p1-p0)
    for threshold in (0,.1,.4,.8,1):
        r = m.evaluate(threshold)
        assert r['replay_reward'] == r['true_reward']
    assert m.evaluate(.8)['trigger_rate'] == 0

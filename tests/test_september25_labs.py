"""September 25: downloadable experiments and consequential boundary cases."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ['linkedin-prediction-to-incrementality', 'angle-tencent-one-step-retrieval',
         'beyond-scalar-dsi-watchtime', 'sgc-state-grounded-conditioning']


def module(slug):
    spec = importlib.util.spec_from_file_location(slug, ROOT/'papers'/slug/'run.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.mark.parametrize('slug', SLUGS)
def test_downloadable_experiment_is_reproducible(slug, tmp_path):
    src = ROOT/'papers'/slug
    shutil.copy2(src/'run.py', tmp_path/'run.py')
    subprocess.run([sys.executable, str(tmp_path/'run.py')], check=True, capture_output=True)
    assert json.loads((tmp_path/'results.json').read_text()) == json.loads((src/'results.json').read_text())
    y = yaml.safe_load((src/'lab.yaml').read_text())
    assert y['source_review']['pdf_sha256'] in (src/'mapping.md').read_text()
    assert y['verification']['mechanism'] == 'PARTIAL'
    assert all(y['verification'][k] == 'NOT TESTED' for k in ['performance','scaling','production_applicability'])


def test_linkedin_budget_is_an_upper_bound_not_spend_target():
    m = module(SLUGS[0])
    assert m.allocate(lambda r:r['mu1']-r['mu0'],0)['selected'] == []
    r = m.allocate(lambda r:r['mu1']-r['mu0'],100)
    assert r['selected'] == ['B','C','D'] and r['cost'] == 4
    for b in range(6):
        prop=m.allocate(lambda r:r['mu1']-r['mu0'],b)
        base=m.allocate(lambda r:r['mu1'],b)
        assert prop['cost'] <= b and prop['incremental_value'] >= base['incremental_value']


def test_angle_filters_invalid_ads_even_in_shared_pair():
    m=module(SLUGS[1])
    ads=[dict(a,valid=False) if a['id']=='B' else a for a in m.ADS]
    assert m.retrieve(ads,1,True)['valid_ads']==['C']
    assert m.retrieve([dict(a,valid=False) for a in ads],3,True)['valid_ads']==[]
    assert m.retrieve([],3,True)['valid_ads']==[]


def test_dsi_distribution_has_information_scalar_cannot_recover():
    m=module(SLUGS[2])
    a,b=[(10,1)],[(0,.5),(20,.5)]
    assert m.summarize(a)['mean_seconds']==m.summarize(b)['mean_seconds']
    assert m.summarize(a)['event_mass']!=m.summarize(b)['event_mass']
    # The shared Bayes-optimal prediction is 1/4; neither endpoint can improve it.
    def risk(q): return (m.expected_brier(a,q,'overplay')+m.expected_brier(b,q,'overplay'))/2
    assert risk(.25)==.1875 < min(risk(0),risk(.5))


def test_sgc_bad_state_is_not_repaired_by_determinism():
    m=module(SLUGS[3])
    live={'A','B','C'}
    assert 'A' not in m.replay(live)['selected']
    assert 'A' in m.replay(live|{'skill-X'})['selected']
    for seed in range(30):
        r=m.replay(live,seed=seed)
        assert r['invalid']==r['consecutive_repeats']==0
        assert r==m.replay(live,seed=seed)
    assert m.freeze_tools('recommend','counter-pick',None)['path']=='fallback'
    assert m.replay(set())['abstentions']==12

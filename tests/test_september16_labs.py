"""Numerical boundaries and information provenance for the three paper-specific probes."""
import importlib.util
import json
from pathlib import Path
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ['univa-commercial-sid-gar','cq-sid-eg-grpo-tmall','intervention-paradox']


def module(slug):
    spec = importlib.util.spec_from_file_location(slug, ROOT/'papers'/slug/'run.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize('slug', SLUGS)
def test_results_and_embedded_widget_are_reproducible(slug):
    p = ROOT/'papers'/slug
    saved = json.loads((p/'results.json').read_text())
    assert module(slug).compute() == saved
    lab = yaml.safe_load((p/'lab.yaml').read_text())
    embedded = lab['sections']['executable_understanding'].split('<script type="application/json" data-probe-data>')[1].split('</script>')[0]
    assert json.loads(embedded) == saved
    assert lab['verification']['performance'] == 'NOT TESTED'
    for name in ('README.md','method.md','mapping.md'):
        assert (p/name).stat().st_size > 100


def test_gar_value_and_validity_are_independent():
    m=module(SLUGS[0])
    assert m.beam(0,1,False)[0]['valid'] is False
    assert m.beam(0,1,True)[0]['path']=='A/a1'
    assert m.beam(.5,1,True)[0]['path']=='B/b1'
    for alpha in (0,.25,.5,1):
        assert all(c['valid'] for c in m.beam(alpha,3,True))
    assert len(m.beam(.5,20,True))==3
    assert m.beam(0,0,True)==[]


def test_cluster_cap_and_group_signal():
    m=module(SLUGS[1])
    assert m.advantages([.1]*8)==[0]*8 or max(map(abs,m.advantages([.1]*8)))<1e-8
    a=m.advantages([.1]*8+[1]*2)
    assert sum(a)==pytest.approx(0,abs=1e-7)
    assert a[0]<0<a[8]
    assert sum(m.split_cluster(5001))==5001
    assert max(m.split_cluster(5001))==51 # Maximum group count prevents a strict 50-item cap.
    assert m.split_cluster(0)==[]
    frames=m.compute()['frames']
    assert frames[2]['target_retained']
    assert not frames[-1]['target_retained']


def test_intervention_conditional_rates_not_event_counts():
    m=module(SLUGS[2])
    # r < d yet benefit: failure and success denominators differ.
    x=m.accounting(78,6,11,5)
    assert x['r'] < x['d']
    assert x['delta'] == pytest.approx(.05)
    assert x['p'] > x['threshold']
    assert m.accounting(0,2,0,48)['r'] is None
    assert m.accounting(45,0,5,0)['d'] is None
    assert m.accounting(25,0,0,25)['threshold'] is None
    assert m.accounting(0,0,0,0)['delta'] is None


def test_source_version_and_attribution_boundaries():
    u=yaml.safe_load((ROOT/'papers'/SLUGS[0]/'lab.yaml').read_text())
    assert 'v2' in u['urls']['pdf']
    assert '5%' in u['sections']['evidence'] and '20%' in u['sections']['evidence']
    c=yaml.safe_load((ROOT/'papers'/SLUGS[1]/'lab.yaml').read_text())
    assert '構成比' in c['sections']['evidence']
    for v in ('50.25','58.96','72.63'):
        assert v in c['sections']['evidence']

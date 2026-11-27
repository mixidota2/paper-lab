"""Test the full text revision, stable calculations, and shared-runner scope."""
import json
from pathlib import Path
import runpy
from xml.etree import ElementTree as E
import pytest
import yaml
from prose_preservation import before_tgr_reader_all_full_prose, before_forecast_critic_all_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/forecast-critic/'
H='papers/_toy_common.py'
FILES={P+n for n in ('lab.yaml','mapping.md','method.md','results.json','run.py','figures/failures.svg','figures/loop.svg','figures/visibility.svg')}|{H}

def pair(p):
    raw=(ROOT/p).read_bytes()
    prior_for_this_test = before_tgr_reader_all_full_prose(ROOT,p,raw) if p == H else raw
    return before_forecast_critic_all_full_prose(ROOT,p,raw),prior_for_this_test

def test_exact_source_scope_and_guard_rejection():
    rows=json.loads((ROOT/'tests/forecast_critic_all_full_prose_hashes.json').read_bytes())['files']
    assert set(rows)==FILES
    for p in FILES:
        a,b=pair(p);assert a!=b
        with pytest.raises(AssertionError):
            before_forecast_critic_all_full_prose(ROOT,p,(ROOT/p).read_bytes()+b'\n')

def test_paper_only_overview_and_figure_geometry():
    a,b=map(yaml.safe_load,pair(P+'lab.yaml'))
    for k in ('id','arxiv_id','authors','status','urls','verification'):
        assert a[k]==b[k]
    s=b['sections'];ov=s['overview']
    assert all(x in ov for x in ('Bhanら','0.88','0.97','0.3417','0.2624','1,000系列'))
    assert all(x not in ov for x in ('Lab','操作','83.3333'))
    assert all(x in s['evidence'] for x in ('8.9%','30.2%','少なくとも10%','0.836'))
    for k in ('failures','loop','visibility'):
        a,b=([ (q.tag,q.attrib) for q in E.fromstring(v).iter()] for v in pair(P+'figures/'+k+'.svg'))
        assert a==b

def test_only_target_generated_prose_changes(tmp_path):
    old=tmp_path/'old.py';old.write_bytes(pair(H)[0])
    recorded=tmp_path/'forecast_critic_stage.py'
    recorded.write_bytes(pair(H)[1])
    a,b=map(runpy.run_path,(str(old),str(recorded)))
    assert tuple(a['SPECS'])==tuple(b['SPECS'])
    for k in a['SPECS']:
        u,v=a['compute'](k),b['compute'](k)
        if k=='forecast-critic':
            assert (u,v)==tuple(map(json.loads,pair(P+'results.json')))
            for result in (u,v):
                result.pop('note')
                result['experiments'][0].pop('name')
                for f in result['explorer']['frames']:
                    f.pop('note')
            assert v['explorer']['frames'][-1]['bars'][0]['value'] is None
        assert u==v,k

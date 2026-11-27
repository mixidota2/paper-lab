from pathlib import Path
from itertools import permutations
from fractions import Fraction
from xml.etree import ElementTree as E
import json, runpy, shutil, subprocess, sys
import yaml
from prose_preservation import before_gryphonilsm_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/gryphon-ilsm/'

def raw(n):
    current=(ROOT/(P+n)).read_bytes()
    return current,before_gryphonilsm_full_prose(ROOT,P+n,current)

def test_gryphon_ilsm_preserves_paper_overview_and_replays_inputs(tmp_path):
    a,b=map(yaml.safe_load,raw('lab.yaml'))
    assert a['sections']['overview']==b['sections']['overview']
    assert a['source_review']==b['source_review'] and a['verification']==b['verification']
    assert [f['path'] for f in a['figures']]==[f['path'] for f in b['figures']]
    for f in a['figures']:
        u,v=map(E.fromstring,raw(f['path']))
        assert u.attrib==v.attrib and u.get('role')=='img'
    a,b=map(json.loads,raw('results.json'))
    assert a.pop('note')!=b.pop('note')
    assert a['experiments'][0].pop('name')!=b['experiments'][0].pop('name')
    assert a==b
    run=tmp_path/'run.py'
    shutil.copyfile(ROOT/(P+'run.py'),run)
    subprocess.run([sys.executable,str(run)],check=True)
    assert (tmp_path/'results.json').read_bytes()==(ROOT/(P+'results.json')).read_bytes()

def test_gryphon_ilsm_ceiling_includes_truth_outside_the_pool():
    exp=runpy.run_path(str(ROOT/(P+'run.py')))['experiment']
    relevant={'B','D'}
    for width in (1,2,3):
        for tie in (False,True):
            x=exp(width,tie)
            for k in (1,2,3,4):
                best=max(Fraction(len(set(order[:k])&relevant),2) for order in permutations(x['pool']))
                assert best==Fraction(min(k,len(set(x['pool'])&relevant)),2)
            assert x['item_recall@2']<=x['reachable_recall_ceiling']
    assert exp(2)['reachable_recall_ceiling']==.5
    assert exp(3)['beam_order'][0]!=exp(3,True)['beam_order'][0]
    assert exp(3)['beam_recall@2']==exp(3,True)['beam_recall@2']==.5
    s=yaml.safe_load((ROOT/(P+'lab.yaml')).read_text())['sections']
    assert all(x in s['evidence'] for x in ['0.8404','3.43ポイント','同等だったとも','最終順位付けモデルは両群で同じ'])

from fractions import Fraction as F
from pathlib import Path
import json, runpy, shutil, subprocess, sys
from xml.etree import ElementTree as E
import yaml
from prose_preservation import before_isd_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/understanding-sids-isd/'
def both(n):
    now=(ROOT/(P+n)).read_bytes()
    return now,before_isd_full_prose(ROOT,P+n,now)

def test_isd_preserves_author_overview_source_values_implementation(tmp_path):
    a,b=map(yaml.safe_load,both('lab.yaml'))
    assert a['sections']['overview']==b['sections']['overview']
    assert a['source_review']==b['source_review'] and a['verification']==b['verification']
    for f0,f1 in zip(a['teaching_figures'],b['teaching_figures'],strict=True):
        assert [x['formula'] for x in f0['steps']]==[x['formula'] for x in f1['steps']]
    for x,y in zip(a['figures'],b['figures'],strict=True):
        assert x['path']==y['path']
        s,t=map(E.fromstring,both(x['path']))
        assert s.attrib==t.attrib and s.get('role')=='img'
    a,b=map(json.loads,both('results.json'))
    assert a.pop('note')!=b.pop('note')
    for x,y in zip(a['experiments'],b['experiments'],strict=True):
        assert x.pop('dataset')!=y.pop('dataset')
    assert a==b
    p=tmp_path/'run.py'
    shutil.copyfile(ROOT/(P+'run.py'),p)
    subprocess.run([sys.executable,str(p)],check=True,capture_output=True)
    assert (tmp_path/'results.json').read_bytes()==(ROOT/(P+'results.json')).read_bytes()

def test_isd_separates_rank_evidence_ties_and_metrics():
    x=runpy.run_path(str(ROOT/(P+'run.py')))
    d=x['decode']
    a=d('x',1,False,False)
    b=d('x',1,True,True)
    assert a['trace'][0]['prefixes']==['0'] and b['trace'][0]['prefixes']==['1']
    assert b['provider']==['e','f','a']
    assert F(1,62)+F(1,61)>F(1,61)+F(1,63)
    real_ranker=d.__globals__['ranker']
    try:
        d.__globals__['ranker']=lambda *args: ['e','a']
        tied=d('x',1,True,False)['trace'][0]
        assert tied['prefixes']==['0']
        assert tied['extensions'][0]['fusion']==tied['extensions'][1]['fusion']
    finally:
        d.__globals__['ranker']=real_ranker
    for h in x['TRAIN']:
        for w in (1,2,4,8):
            for s in (False,True):
                f,g=d(h,w,s,False),d(h,w,s,True)
                assert f['trace']==g['trace'] and set(f['ranked_items'])==set(g['ranked_items'])
    s=yaml.safe_load((ROOT/(P+'lab.yaml')).read_text())['sections']
    assert all(n in s['evidence'] for n in ('99.57%','99.51%','35.4%','24.4%','0.1291から0.1266'))
    assert 'Kℓと、Labの全9件' in s['executable_understanding']

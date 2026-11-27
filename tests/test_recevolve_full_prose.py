"""Checks for the paper summary, evidence and unchanged deterministic experiment."""
import json
from pathlib import Path
import runpy
import xml.etree.ElementTree as ET

import yaml
from prose_preservation import before_recevolve_full_prose

ROOT=Path(__file__).resolve().parents[1]
REL='papers/recevolve-autonomous-rec/'
P=ROOT/REL

def before(name):
    return before_recevolve_full_prose(ROOT,REL+name,(P/name).read_bytes())

def test_recevolve_deterministic_results_and_conditions():
    new=json.loads((P/'results.json').read_bytes())
    assert new==runpy.run_path(str(P/'run.py'))['compute']()
    old=json.loads(before('results.json'))
    for d in (old,new):
        del d['note'],d['experiments'][0]['name'],d['experiments'][0]['dataset']
        for k in ('guarded_trace','unguarded_trace'):
            for row in d[k]: del row['reason']
    assert new==old
    model=runpy.run_path(str(P/'run.py'))
    decide=model['decide']
    base=dict(valid=True,success=True,candidates=8000,ndcg=.4,aux=.6)
    assert decide(base,base|dict(ndcg=base['ndcg']+.001))[0]=='ROLLBACK'
    assert decide(base,base|dict(ndcg=.42,aux=.5))[0]=='KEEP'
    assert decide(base,base|dict(ndcg=.42,aux=.4999))[0]=='ROLLBACK'
    assert new['guarded_trace'][2]['status']=='ROLLBACK'
    assert new['unguarded_trace'][2]['status']=='KEEP'

def test_recevolve_paper_only_overview_and_metrics():
    d=yaml.safe_load((P/'lab.yaml').read_bytes())
    old=yaml.safe_load(before('lab.yaml'))
    s=d['sections']
    for k in ('id','authors','title','urls','verification','verdict','status'):
        assert d[k]==old[k]
    for now,prev in zip(d['teaching_figures'],old['teaching_figures'],strict=True):
        for k in ('id','kind','after','locator'):
            assert now[k]==prev[k]
        assert [x['formula'] for x in now.get('steps',[])]==[x['formula'] for x in prev.get('steps',[])]
        assert [x['value'] for x in now.get('bars',[])]==[x['value'] for x in prev.get('bars',[])]
    a=s['overview']
    assert len(a.strip().split('\n\n'))==2
    assert all(t in a for t in ('41件','0.4796から0.5751','3.77%','人間','試行は元に戻し','二塔型モデル'))
    assert all(t not in a for t in ('Lab','人工','run.py','<figure','<table','動画'))
    e=s['evidence']
    assert all(t in e for t in ('一次資料','0.4440','MAP@50','200万ステップ','7.44%','−16.50%','新しいコンテンツ'))
    separate=s['executable_understanding']
    assert '正例が50位に入らなかった検索は、NDCG@50を0として平均に含めます' in separate
    assert 'Labの提案' in s['results']

def test_recevolve_two_accessible_diagrams():
    for n in ('lifecycle.svg','candidate-set.svg'):
        root=ET.parse(P/'figures'/n).getroot()
        assert root.attrib['role']=='img' and root.attrib['aria-labelledby']=='title desc'
        text=' '.join(t for t in root.itertext() if t)
        if n=='lifecycle.svg':
            assert all(x in text for x in ('両方を満たす','変更を記録','変更前の基準に戻す'))
        else:
            assert all(x in text for x in ('8,000','1,000','7,999','点の数や間隔','人間が'))

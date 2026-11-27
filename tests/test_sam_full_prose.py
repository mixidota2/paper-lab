from pathlib import Path
import ast
import json
import shutil
import subprocess
import sys
import runpy
import yaml

from prose_preservation import before_sam_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/sam-d2q-aliexpress-doc2query/'
def files(name):
    cur=(ROOT/(P+name)).read_bytes()
    return cur,before_sam_full_prose(ROOT,P+name,cur)

def test_sam_preserves_paper_overview_equations_and_evidence_boundaries():
    new,old=map(yaml.safe_load,files('lab.yaml'))
    assert new['sections']['overview']==old['sections']['overview']
    assert (ROOT/(P+'README.md')).read_text().count(new['sections']['overview'])==1
    assert new['verification']==old['verification']
    assert [r['formula'] for r in new['teaching_figures'][1]['steps']]==[r['formula'] for r in old['teaching_figures'][1]['steps']]
    assert [r['value'] for r in new['teaching_figures'][2]['bars']]==[r['value'] for r in old['teaching_figures'][2]['bars']]
    assert all(s in new['sections']['evidence'] for s in ['2.07%から1.72%','0.35ポイント','0.2%増えた','2025年8〜11月','95%水準'])
    assert '商品を1件ずつ調べ' in new['sections']['executable_understanding']
    assert '転置索引そのものや、検索速度を再現する実験ではない' in new['sections']['executable_understanding']

def test_sam_preserves_all_control_outputs_and_searches_product_sets(tmp_path):
    new,old=map(json.loads,files('results.json'))
    assert new['modes']==old['modes'] and new['verification']==old['verification']
    for a,b in zip(new['explorer']['frames'],old['explorer']['frames'],strict=True):
        assert a['value']==b['value'] and a['bars']==b['bars']
    run=tmp_path/'run.py'
    shutil.copyfile(ROOT/(P+'run.py'),run)
    subprocess.run([sys.executable,str(run)],check=True)
    assert (tmp_path/'results.json').read_bytes()==(ROOT/(P+'results.json')).read_bytes()
    r=runpy.run_path(str(run))
    terms=set('red leather bag'.split())
    assert all(not terms <= set(q.split()) for q,v in r['CANDIDATES']['a'])
    index={k:set(v.split()) for k,v in r['ITEMS'].items()}
    assert not r['retrieve'](index,'red leather bag')
    for q,v in r['CANDIDATES']['a']:
        index['a'].update(q.split())
    assert r['retrieve'](index,'red leather bag')=={'a'}
    assert r['retrieve'](index,'red')=={'a'}
    assert r['retrieve'](index,'red nonexistent')==set()

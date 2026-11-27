from pathlib import Path
import ast
import importlib.util
import json
import shutil
import subprocess
import sys
import yaml
from prose_preservation import before_muser_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/muser-baidu-long-sequence-multi-interest/'
def files(name):
    cur=(ROOT/(P+name)).read_bytes()
    return cur,before_muser_full_prose(ROOT,P+name,cur)

def test_muser_preserves_author_summary_figures_and_comparisons():
    new,old=map(yaml.safe_load,files('lab.yaml'))
    assert new['sections']['overview']==old['sections']['overview']
    assert new['sections']['overview'] in (ROOT/P/'README.md').read_text()
    assert new['verification']==old['verification']
    assert new['source_review']==old['source_review']
    assert [x['id'] for x in new['teaching_figures']]==[x['id'] for x in old['teaching_figures']]
    for i in (0,2):
        assert [r['formula'] for r in new['teaching_figures'][i]['steps']]==[r['formula'] for r in old['teaching_figures'][i]['steps']]
    assert [r['value'] for r in new['teaching_figures'][1]['bars']]==[r['value'] for r in old['teaching_figures'][1]['bars']]
    assert all(p in new['sections']['evidence'] for p in ('1.19ポイント低く','4.83ポイント高い','従来の平坦なHNSW','圧縮だけの効果とは扱わない'))

def test_muser_preserves_artifacts_and_denominator(tmp_path):
    result,old_result=files('results.json')
    a,b=map(json.loads,(result,old_result))
    assert a.pop('note')!=b.pop('note') and a==b
    def stripped(source):
        t=ast.parse(source)
        t.body=t.body[1:]
        for n in ast.walk(t):
            if isinstance(n,ast.keyword) and n.arg=='note':
                assert isinstance(n.value,ast.Constant)
                n.value=ast.Constant('display')
        return ast.dump(t)
    assert stripped(files('run.py')[0])==stripped(files('run.py')[1])
    run=tmp_path/'run.py'
    shutil.copyfile(ROOT/P/'run.py',run)
    subprocess.run([sys.executable,str(run)],check=True)
    assert (tmp_path/'results.json').read_bytes()==result
    s=importlib.util.spec_from_file_location('muser_synthetic',run)
    m=importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    assert m.orthogonal_penalty([[2,0],[1,0]])==2.0
    assert m.orthogonal_penalty([[1,0],[1,0]])==0.5
    assert m.pool([1,0],2)==m.pool([0,1],2)

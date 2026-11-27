from __future__ import annotations
import ast
import json
import shutil
import subprocess
import sys
from pathlib import Path
import yaml

from prose_preservation import before_varg_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/varg-tmall-value-generative-retrieval/'
def files(name):
    current=(ROOT/(P+name)).read_bytes()
    return current,before_varg_full_prose(ROOT,P+name,current)

def test_varg_primary_overview_formulas_and_scopes():
    new,old=map(yaml.safe_load,files('lab.yaml'))
    assert new['sections']['overview']==old['sections']['overview']
    assert new['sections']['overview'] in (ROOT/P/'README.md').read_text()
    assert new['source_review']==old['source_review']
    assert new['verification']==old['verification']
    figs=new['teaching_figures']
    was=old['teaching_figures']
    assert [f['id'] for f in figs]==[f['id'] for f in was]
    assert [s['formula'] for s in figs[1]['steps']]==[s['formula'] for s in was[1]['steps']]
    assert [r['cells'][:4] for r in figs[2]['rows']]==[r['cells'][:4] for r in was[2]['rows']]
    for fragment in ('通過する段を変えただけの試験ではない','2.19ポイント','0.21ポイント','0.08ポイント','91.25%','1.45%'):
        assert fragment in new['sections']['evidence']

def test_varg_exact_rerun_and_item_counts(tmp_path):
    def normal(raw):
        x=json.loads(raw)
        x.pop('note')
        x['experiments'][0].pop('name')
        return x
    current,old=files('results.json')
    assert normal(current)==normal(old)
    v=normal(current)
    assert v['maps']['frozen']=={'A':0,'D':1,'B':1,'C':2}
    assert v['experiments'][0]['metrics']['alias_item_rate']['frozen']==.5
    def program(raw):
        r=ast.parse(raw)
        r.body=r.body[1:]
        for node in ast.walk(r):
            if isinstance(node,ast.Dict):
                for i,k in enumerate(node.keys):
                    if isinstance(k,ast.Constant) and k.value in ('note','name'):
                        assert isinstance(node.values[i],ast.Constant)
                        node.values[i]=ast.Constant('display')
        return ast.dump(r)
    assert program(files('run.py')[0])==program(files('run.py')[1])
    run=tmp_path/'run.py'
    shutil.copyfile(ROOT/P/'run.py',run)
    subprocess.run([sys.executable,str(run)],check=True)
    assert (tmp_path/'results.json').read_bytes()==current

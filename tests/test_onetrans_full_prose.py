import ast
import json
from pathlib import Path
import subprocess
import sys

import yaml

from prose_preservation import before_onetrans_full_prose

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'papers/onetrans-v2-cascade-unification/'

def pair(name):
    path=PREFIX+name
    new=(ROOT/path).read_bytes()
    return before_onetrans_full_prose(ROOT,path,new),new

def test_onetrans_paper_summary_and_figure_mechanics_are_preserved():
    a,b=map(yaml.safe_load,pair('lab.yaml'))
    assert a['sections']['overview']==b['sections']['overview']
    overview=b['sections']['overview'].encode()
    for readme in pair('README.md'):
        assert readme.count(overview)==1
    assert a['verification']==b['verification']
    old,new=a['teaching_figures'],b['teaching_figures']
    assert [f['id'] for f in new]==['cache','dcgr','hr']
    for x,y in zip(old,new):
        assert {k:x[k] for k in ('kind','id','source','after','locator')}=={k:y[k] for k in ('kind','id','source','after','locator')}
    assert [r['label'] for r in old[0]['rows']]==[r['label'] for r in new[0]['rows']]
    assert [s['formula'] for s in old[1]['steps']]==[s['formula'] for s in new[1]['steps']]
    assert old[2]['bars']==new[2]['bars']
    assert '1.53倍' in b['sections']['evidence'] and '3.2倍' in b['sections']['evidence']

def test_onetrans_standalone_toy_changes_only_its_explanation(tmp_path):
    a,b=map(json.loads,pair('results.json'))
    assert a.pop('note') != b.pop('note')
    assert a==b
    assert [r['ranking'][0]['item'] for r in b['frames']]==['A','A','B','C']
    assert b['cache_cost']=={'separate':360,'shared':160}
    def norm(raw):
        t=ast.parse(raw)
        assert isinstance(t.body.pop(0), ast.Expr)
        for stmt in t.body[-1].body:
            if isinstance(stmt, ast.Assign) and any(isinstance(t,ast.Subscript) and t.slice.value=='note' for t in stmt.targets):
                stmt.value=ast.Constant(value='')
        return ast.dump(t,include_attributes=False)
    old,new=pair('run.py')
    assert norm(old)==norm(new)
    (tmp_path/'run.py').write_bytes(new)
    subprocess.run([sys.executable,'-S','run.py'],cwd=tmp_path,check=True)
    assert (tmp_path/'results.json').read_bytes()==pair('results.json')[1]


def test_only_onetrans_widget_copy_changes():
    from paper_lab.batch28 import widget
    name='paper_lab/batch28.py'
    new=(ROOT/name).read_bytes()
    old=before_onetrans_full_prose(ROOT,name,new)
    namespace={}
    exec(compile(old,name,'exec'),namespace)
    cases=('reasoncast-agentic-demand-forecasting','scope-coupled-supply-chain-policies',
           'evaluation-choices-forecasting-leaderboard','harness-zero-distillation','onetrans-v2-cascade-unification')
    for slug in cases:
        d=json.loads((ROOT/'papers'/slug/'results.json').read_text())
        was,now=namespace['widget'](d),widget(d)
        if slug.endswith('cascade-unification'):
            assert was!=now and '加点の強さ（β）' in now
            for label in ('β = 0','β = 0.5','β = 1','β = 2','候補 A','候補 B','候補 C'):
                assert label in now
        else:
            assert was==now,slug

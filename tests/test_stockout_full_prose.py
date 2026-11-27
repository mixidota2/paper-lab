import ast
import json
from pathlib import Path
import subprocess
import sys
import yaml

from prose_preservation import before_stockout_full_prose

ROOT=Path(__file__).resolve().parents[1]
PREFIX='papers/stockout-data-debt/'

def pair(name):
    path=PREFIX+name
    new=(ROOT/path).read_bytes()
    return before_stockout_full_prose(ROOT,path,new),new

def test_the_overview_and_figure_numbers_stay_unchanged():
    a,b=map(yaml.safe_load,pair('lab.yaml'))
    assert a['sections']['overview']==b['sections']['overview']
    assert a['verification']==b['verification']
    for key in ('id','arxiv_id','urls','topics','figures'):
        assert a[key]==b[key]
    assert a['teaching_figures'][1]['columns']==b['teaching_figures'][1]['columns']
    assert a['teaching_figures'][1]['rows']==b['teaching_figures'][1]['rows']

def test_only_display_text_changes_and_the_replay_stays_exact(tmp_path):
    a,b=map(json.loads,pair('results.json'))
    def strip_display(d):
        del d['note']
        for item in d['experiments']: del item['name']
        e=d['explorer']
        assert e['default']==5
        del e['label'],e['metric']
        for frame in e['frames']:
            del frame['note']
            for bar in frame['bars']: del bar['label']
    for d in (a,b): strip_display(d)
    assert a==b
    assert [f['value'] for f in b['explorer']['frames']]==[1,2,3,5,7,11,21]
    assert b['calculations'][5]['worst_regret']==[.25,.25]
    assert b['carryover']['data_debt']==.1225
    run_before,run_after=pair('run.py')
    def numeric_code(raw):
        tree=ast.parse(raw)
        assert isinstance(tree.body.pop(0),ast.Expr)
        output=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.FunctionDef) and n.name=='results')
        tree.body.pop(output)
        return ast.dump(tree,include_attributes=False)
    assert numeric_code(run_before)==numeric_code(run_after)
    (tmp_path/'run.py').write_bytes(run_after)
    subprocess.run([sys.executable,'-S','run.py'],cwd=tmp_path,check=True)
    assert (tmp_path/'results.json').read_bytes()==pair('results.json')[1]

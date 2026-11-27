"""Keep the current publication's paper summary and durable input behavior separate."""
import ast
import json
import re
from pathlib import Path
import subprocess
import sys

import pytest
import yaml
from prose_preservation import before_reasoncast_all_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/reasoncast-agentic-demand-forecasting/'
W='paper_lab/batch28.py'
FILES={P+n for n in 'README.md interactive.html interactive.js lab.yaml mapping.md method.md model.js results.json run.py'.split()}|{W}

def pair(path):
    raw=(ROOT/path).read_bytes()
    return before_reasoncast_all_full_prose(ROOT,path,raw),raw

def test_every_prose_source_uses_exact_revision():
    assert set(json.loads((ROOT/'tests/reasoncast_all_full_prose_hashes.json').read_bytes())['files'])==FILES
    for path in FILES:
        assert pair(path)[0]!=pair(path)[1]
        with pytest.raises(AssertionError):
            before_reasoncast_all_full_prose(ROOT,path,pair(path)[1]+b'\n')

def test_paper_summary_and_technical_figure_values():
    old,y=map(yaml.safe_load,pair(P+'lab.yaml'))
    assert all(old[k]==y[k] for k in ('arxiv_id','authors','title','status','urls','verification'))
    s=y['sections']
    for t in ('Yangら','33.10%','32.63%','7.91%','9.59%','補正を見送らない'):
        assert t in s['overview']
    assert not any(t in s['overview'] for t in ('Lab','教材','29.289322'))
    assert all(t in s['evidence'] for t in ('15,696','3,049','15期間中13期間','ツール呼び出し頻度'))
    for a,b in zip(old['teaching_figures'],y['teaching_figures'],strict=True):
        for k in ('id','source','after','bars','maximum'):
            assert a.get(k)==b.get(k)
        assert [x['formula'] for x in a.get('steps',())]==[x['formula'] for x in b.get('steps',())]

def test_fixed_input_rules_and_rebuilt_data(tmp_path):
    def computation(v):
        t=ast.parse(v)
        for n in ast.walk(t):
            if isinstance(n,(ast.Module,ast.FunctionDef)) and n.body and isinstance(n.body[0],ast.Expr) and isinstance(n.body[0].value,ast.Constant) and isinstance(n.body[0].value.value,str):
                del n.body[0]
            if isinstance(n,ast.Assign) and any(isinstance(k,ast.Subscript) and isinstance(k.slice,ast.Constant) and k.slice.value=='note' for k in n.targets):
                n.value.value=''
        return ast.dump(t)
    a,b=map(computation,pair(P+'run.py'))
    assert a==b
    a,b=map(json.loads,pair(P+'results.json'))
    assert a.pop('note')!=b.pop('note') and a==b
    p=tmp_path/'run.py';p.write_bytes(pair(P+'run.py')[1])
    subprocess.run([sys.executable,str(p)],check=True)
    assert (tmp_path/'results.json').read_bytes()==pair(P+'results.json')[1]
    a,b=pair(P+'model.js')
    assert re.sub(rb'  // .*\n',b'',b,count=1)==a

def test_sibling_widgets_exact_and_control_values_fixed():
    def render(raw):
        ns={}
        exec(compile(raw,W,'exec'),ns)
        return ns['widget']
    a,b=map(render,pair(W))
    for slug in ('scope-coupled-supply-chain-policies','onetrans-v2-cascade-unification',
                 'evaluation-choices-forecasting-leaderboard','harness-zero-distillation'):
        j=json.loads((ROOT/'papers'/slug/'results.json').read_bytes())
        assert a(j)==b(j)
    a,b=pair(P+'interactive.html')
    assert re.findall(rb'(?:name|value|src)="[^"]+"',a)==re.findall(rb'(?:name|value|src)="[^"]+"',b)
    assert b.count(b'data-guess')==1

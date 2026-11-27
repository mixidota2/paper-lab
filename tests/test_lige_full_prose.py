from __future__ import annotations
import ast
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from prose_preservation import before_lige_full_prose

ROOT=Path(__file__).resolve().parents[1]
PREFIX='papers/lige-gr-meta-listwise/'
SRC=ROOT/PREFIX


def get_files(name):
    raw=(SRC/name).read_bytes()
    earlier=before_lige_full_prose(ROOT,PREFIX+name,raw)
    return raw,earlier


def test_lige_preserves_overview_and_paper_scope():
    new,old=map(yaml.safe_load,get_files('lab.yaml'))
    assert new['sections']['overview']==old['sections']['overview']
    assert new['sections']['overview'] in (SRC/'README.md').read_text()
    assert new['source_review']==old['source_review']
    assert new['verification']==old['verification']
    assert [f['id'] for f in new['teaching_figures']]==[f['id'] for f in old['teaching_figures']]
    assert [s['formula'] for s in new['teaching_figures'][0]['steps']]==[s['formula'] for s in old['teaching_figures'][0]['steps']]
    evidence=new['sections']['evidence']
    assert '一次資料' in evidence
    assert all(v in evidence for v in ('0.05%','0.69%','1.14%増には足せない'))
    assert '2つの変更を一緒に入れた' in evidence


def test_lige_numeric_computation_unchanged_and_timeout_counts_attempt():
    def numeric(b):
        result=json.loads(b)
        del result['note']
        return result
    result,prev_result=get_files('results.json')
    assert numeric(result)==numeric(prev_result)

    def executable_ast(b):
        node=ast.parse(b)
        node.body=node.body[1:]
        for d in ast.walk(node):
            if isinstance(d,ast.Dict):
                for key,value in zip(d.keys,d.values):
                    if isinstance(key,ast.Constant) and key.value=='note':
                        assert isinstance(value,ast.Constant)
                        value.value=''
        return ast.dump(node)
    program,prev_program=get_files('run.py')
    assert executable_ast(program)==executable_ast(prev_program)
    spec=importlib.util.spec_from_file_location('lige_synthetic_exec',SRC/'run.py')
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert m.compute()==json.loads(result)
    calls=[]
    original=m.score
    def score(path,contextual=True,survival=True):
        calls.append((tuple(path),contextual,survival))
        return original(path,contextual,survival)
    m.score=score
    fallback=m.decode(beam=6,mode='duration',budget=2)
    boundary=next(i for i,(_,contextual,survival) in enumerate(calls) if not contextual and not survival)
    assert calls[:boundary]==[((0,),True,True),((1,),True,True)]
    assert fallback['aborted_evaluations']==3 and fallback['evaluations']==17
    assert '2通りを評価した後、3通り目を評価する前' in (SRC/'method.md').read_text()


def test_lige_run_writes_exact_download(tmp_path):
    run=tmp_path/'run.py'
    shutil.copyfile(SRC/'run.py',run)
    completed=subprocess.run([sys.executable,str(run)],capture_output=True,check=True)
    assert completed.stdout==(SRC/'results.json').read_bytes()==(tmp_path/'results.json').read_bytes()

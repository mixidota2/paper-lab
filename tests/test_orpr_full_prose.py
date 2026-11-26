"""Protect ORPR calculations and the other labs using the shared renderer."""
import ast
from pathlib import Path
import json
import subprocess

import pytest
import yaml
from prose_preservation import before_orpr_full_prose, before_proximal_full_prose, orpr_full_prose_hash

ROOT = Path(__file__).resolve().parents[1]
BASE = 'c2e4172a0f3e7ab083dcfee9be7619575074a0dd'
PREFIX = 'papers/orpr-or-guided-pretrain-reinforce-inventory'


def historical(path):
    return subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT)


def test_exact_archive_and_orpr_only_shared_copy():
    paths = {f'{PREFIX}/{name}' for name in ('README.md','lab.yaml','mapping.md','method.md','results.json','run.py')}
    shared = 'paper_lab/inventory02.py'
    rows = json.loads((ROOT/'tests/orpr_full_prose_hashes.json').read_text())['files']
    assert rows.keys() == paths | {shared}
    for path,row in rows.items():
        new = before_proximal_full_prose(ROOT, path, (ROOT/path).read_bytes())
        assert new != historical(path)
        assert before_orpr_full_prose(ROOT,path,new)==historical(path)
        with pytest.raises(AssertionError):
            before_orpr_full_prose(ROOT,path,new+b'\n')
        for alg in ('sha256','blob'):
            assert orpr_full_prose_hash(ROOT,path,row['before'][alg],alg)==row['after'][alg]
            with pytest.raises(AssertionError):
                orpr_full_prose_hash(ROOT,path,row['after'][alg],alg)
    def excluded(raw):
        head,tail = raw.split(b'def orpr(r):',1)
        return head,tail.split(b'\ndef proximal(r):',1)[1]
    assert excluded(before_proximal_full_prose(ROOT, shared, (ROOT/shared).read_bytes())) == excluded(historical(shared))


def test_orpr_math_data_and_canonical_overview_did_not_change():
    p=f'{PREFIX}/lab.yaml'
    a,b=map(yaml.safe_load,(historical(p),(ROOT/p).read_bytes()))
    assert a['sections']['overview']==b['sections']['overview']
    assert a['sections'].keys()==b['sections'].keys()
    for fig,new in zip(a['teaching_figures'],b['teaching_figures'],strict=True):
        assert all(fig[k]==new[k] for k in ('id','kind','after','source'))
        assert [s['formula'] for s in fig.get('steps',())]==[s['formula'] for s in new.get('steps',())]
    p=f'{PREFIX}/results.json'
    x,y=map(json.loads,(historical(p),(ROOT/p).read_bytes()))
    assert x.pop('note') != y.pop('note')
    for r in (x,y):
        r['experiments'][0].pop('name')
    assert x==y
    p=f'{PREFIX}/run.py'
    def numeric_logic(raw):
        tree=ast.parse(raw)
        for n in ast.walk(tree):
            if isinstance(n,(ast.Module,ast.FunctionDef)) and ast.get_docstring(n):
                n.body=n.body[1:]
            if isinstance(n,ast.keyword) and n.arg in ('note','name'):
                n.value=ast.Constant(None)
        return ast.dump(tree)
    assert numeric_logic(historical(p))==numeric_logic((ROOT/p).read_bytes())

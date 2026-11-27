from pathlib import Path
import ast
import json

import pytest
import yaml

from prose_preservation import before_sparse_reader_all_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/tsfm-sparse-event-ranking/'


def pair(name):
    final=(ROOT/(P+name)).read_bytes()
    return before_sparse_reader_all_full_prose(ROOT,P+name,final),final


def test_sparse_text_and_primary_overview_boundaries():
    rows=json.loads((ROOT/'tests/sparse_reader_all_full_prose_hashes.json').read_bytes())['files']
    assert set(rows)=={P+n for n in ('lab.yaml','results.json','run.py')}
    for n in rows:
        a,b=pair(n.removeprefix(P))
        assert a!=b
        with pytest.raises(AssertionError):
            before_sparse_reader_all_full_prose(ROOT,n,b+b'\n')
    a,b=map(yaml.safe_load,pair('lab.yaml'))
    old=a['sections'].pop('overview')
    new=b['sections'].pop('overview')
    assert a.pop('summary')!=b.pop('summary')
    assert a==b and old!=new
    assert all(v in new for v in ('64時点','正の値と0が両方','最大0.031','30組中29組','6モデルすべて','LightGBM'))
    assert not any(v in new for v in ('Lab','教材','<figure','<table'))


def test_sparse_runner_numeric_frames_match_before():
    a,b=map(json.loads,pair('results.json'))
    aliases={b[k]:a[k] for k in ('kind','reported_source')}
    for l,r in zip(a['scenarios'],b['scenarios'],strict=True):
        for p,q in zip(l['rows'],r['rows'],strict=True):
            aliases[q['method']]=p['method']
    assert len(aliases)==6
    def restore(v):
        if isinstance(v,str):return aliases.get(v,v)
        if isinstance(v,list):return [restore(u) for u in v]
        if isinstance(v,dict):return {key:restore(u) for key,u in v.items()}
        return v
    assert a==restore(b)
    class Invert(ast.NodeTransformer):
        def visit_Constant(self,n):
            if isinstance(n.value,str):n.value=aliases.get(n.value,n.value)
            return n
    def clean(raw):
        tree=ast.parse(raw)
        assert isinstance(tree.body.pop(0).value,ast.Constant)
        return ast.dump(Invert().visit(tree))
    a,b=pair('run.py')
    assert a.splitlines()[:4]==b.splitlines()[:4]
    assert clean(a)==clean(b)

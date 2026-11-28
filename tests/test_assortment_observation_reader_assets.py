"""The reader copy changes without changing any arithmetic or widget controls."""
import ast
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from prose_preservation import (
    before_assortment_observation_reader_assets,
    assortment_observation_reader_assets_rows,
    assortment_observation_reader_assets_hash,
)

ROOT=Path(__file__).resolve().parents[1]
PREFIX='papers/assortment-observation-budget/'
RENDERER='paper_lab/assortment_observation.py'


def test_exact_assortment_reader_assets():
    rows=assortment_observation_reader_assets_rows(ROOT)
    assert rows.keys() == {RENDERER} | {PREFIX+n for n in (
        'README.md','evidence.md','experiment.md','interactive.html',
        'interactive.js','lab.yaml','mapping.md','method.md','results.json','run.py',
    )}
    for path,row in rows.items():
        now=(ROOT/path).read_bytes()
        prior=before_assortment_observation_reader_assets(ROOT,path,now)
        assert hashlib.sha256(now).hexdigest()==row['after_sha256']
        assert hashlib.sha256(prior).hexdigest()==row['before_sha256']
        for text,label in ((now,'after_blob'),(prior,'before_blob')):
            assert hashlib.sha1(f'blob {len(text)}\0'.encode()+text).hexdigest()==row[label]
        for algorithm in ('sha256','blob'):
            assert assortment_observation_reader_assets_hash(ROOT,path,row['before_'+algorithm],algorithm)==row['after_'+algorithm]
            if row['prior_spans']:
                with pytest.raises(AssertionError):
                    assortment_observation_reader_assets_hash(ROOT,path,'0'*len(row['before_'+algorithm]),algorithm)
        with pytest.raises(AssertionError):
            before_assortment_observation_reader_assets(ROOT,path,now+b'\n')


def test_assortment_source_and_calculations_unchanged_except_prose():
    def contents(name):
        path=PREFIX+name
        now=(ROOT/path).read_bytes()
        return before_assortment_observation_reader_assets(ROOT,path,now),now

    def python_logic(data):
        tree=ast.parse(data)
        for node in ast.walk(tree):
            if isinstance(node,(ast.Module,ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                node.body=[stmt for stmt in node.body
                           if not (isinstance(stmt,ast.Expr) and
                                   isinstance(stmt.value,ast.Constant) and isinstance(stmt.value.value,str))]
            if isinstance(node,ast.keyword) and node.arg=='limits':
                assert isinstance(node.value,ast.List) and len(node.value.elts)==2
                assert all(isinstance(x,ast.Constant) and isinstance(x.value,str) for x in node.value.elts)
                node.value=ast.Constant(value='<reader explanation only>')
        return ast.dump(tree)

    assert len({python_logic(b) for b in contents('run.py')}) == 1
    previous, live=map(json.loads,contents('results.json'))
    assert previous.pop('limits') != live.pop('limits')
    assert previous == live and len(live['cases']) == 96
    for name in ('interactive.html','interactive.js','README.md','experiment.md','mapping.md','method.md'):
        assert len(set(contents(name))) == 1
    past,new=map(yaml.safe_load,contents('lab.yaml'))
    old_overview=past['sections'].pop('overview')
    overview=new['sections'].pop('overview')
    assert past==new and overview!=old_overview
    assert all(term in overview for term in ('多項ロジット','顧客1人','同じ品揃え','より収益が低い商品を含まない品揃え','ゼロに近づく'))
    assert 'Lab' not in overview
    evidence=contents('evidence.md')[1].decode()
    assert all(term in evidence for term in ('Theorem 6.3','n−1種類','商品1・3と商品2・3'))

"""Check exact prose updates and preserve all model and widget calculations."""
import ast
import hashlib
from pathlib import Path
import re

import pytest
import yaml

from prose_preservation import (
    before_perishables_reader_assets, perishables_reader_assets_rows,
    perishables_reader_assets_hash,
)

ROOT=Path(__file__).resolve().parents[1]
PREFIX='papers/discounted-perishables-forecast/'


def test_exact_perishables_reader_asset_transitions():
    rows=perishables_reader_assets_rows(ROOT)
    assert rows.keys() == {PREFIX+n for n in (
        'README.md','evidence.md','experiment.md','interactive.html',
        'interactive.js','lab.yaml','mapping.md','method.md','model.js','results.json','run.py',
    )}
    for path,row in rows.items():
        present=(ROOT/path).read_bytes()
        earlier=before_perishables_reader_assets(ROOT,path,present)
        assert hashlib.sha256(present).hexdigest()==row['after_sha256']
        assert hashlib.sha256(earlier).hexdigest()==row['before_sha256']
        for algorithm in ('sha256','blob'):
            assert perishables_reader_assets_hash(ROOT,path,row['before_'+algorithm],algorithm)==row['after_'+algorithm]
            with pytest.raises(AssertionError):
                perishables_reader_assets_hash(ROOT,path,'0'*len(row['before_'+algorithm]),algorithm)
        with pytest.raises(AssertionError):
            before_perishables_reader_assets(ROOT,path,present+b'\n')


def test_only_explanatory_content_changed():
    def contents(name):
        path=PREFIX+name
        now=(ROOT/path).read_bytes()
        return before_perishables_reader_assets(ROOT,path,now),now

    def python_logic(data):
        tree=ast.parse(data)
        for node in ast.walk(tree):
            if isinstance(node,(ast.Module,ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and ast.get_docstring(node) is not None:
                del node.body[0]
        return ast.dump(tree)

    assert len({python_logic(b) for b in contents('run.py')}) == 1
    assert len({re.sub(rb'^\s*//[^\n]*\n',b'',b,flags=re.M) for b in contents('model.js')})==1
    assert len({re.sub(rb"(?<=:)'[^'\n]+'",b"''",b) for b in contents('interactive.js')})==1
    assert len(set(contents('interactive.html'))) == 1
    assert len(set(contents('results.json'))) == 1
    past,new=map(yaml.safe_load,contents('lab.yaml'))
    assert past.keys()==new.keys() and past['sections'].keys()==new['sections'].keys()
    assert {k for k in new if new[k]!=past[k]}=={'summary','sections'}
    assert {k for k in new['sections'] if new['sections'][k]!=past['sections'][k]}=={'overview','results'}
    overview=new['sections']['overview']
    assert all(term in overview for term in ('676店舗','1,077品目','92.2%','回帰','値引き価格で出したか'))
    assert 'Lab' not in overview

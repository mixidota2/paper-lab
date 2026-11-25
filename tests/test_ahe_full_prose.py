"""Pin exact AHE prose and unchanged receipt logic."""
import ast
from hashlib import sha1, sha256
from pathlib import Path
import json
import re

import pytest
import yaml
from prose_preservation import before_ahe_full_prose, ahe_full_prose_hash

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/ahe-beta-receipt/'
NAMES = ('README.md', 'method.md', 'mapping.md', 'lab.yaml', 'run.py', 'results.json')


def identities(data):
    return {'blob':sha1(f'blob {len(data)}\0'.encode()+data).hexdigest(),'sha256':sha256(data).hexdigest()}


def test_exact_ahe_prose_mapping_and_mutation_guard():
    snapshots=json.loads((ROOT/'tests/ahe_full_prose_hashes.json').read_text())['files']
    assert set(snapshots)=={P+name for name in NAMES}
    for path,row in snapshots.items():
        after=(ROOT/path).read_bytes()
        before=before_ahe_full_prose(ROOT,path,after)
        for alg in ('blob','sha256'):
            a,b=identities(before)[alg],identities(after)[alg]
            assert (a,b)==(row['before_'+alg],row['after_'+alg])
            assert ahe_full_prose_hash(ROOT,path,a,alg)==b
            with pytest.raises(AssertionError):
                ahe_full_prose_hash(ROOT,path,b,alg)
        with pytest.raises(AssertionError):
            before_ahe_full_prose(ROOT,path,after+b'\n')
        assert re.findall(rb'\]\(([^)]+)\)',before)==re.findall(rb'\]\(([^)]+)\)',after)


def test_overview_and_binary_conditions_unchanged():
    def pair(name):
        path=P+name
        after=(ROOT/path).read_bytes()
        return before_ahe_full_prose(ROOT,path,after),after
    old,new=map(yaml.safe_load,pair('lab.yaml'))
    assert old.keys()==new.keys()
    assert all(old[k]==new[k] for k in old if k not in ('core_idea','sections','teaching_figures','interactives'))
    assert old['sections'].keys()==new['sections'].keys()
    assert all(old['sections'][k]==new['sections'][k] for k in ('overview','method','mapping'))
    for a,b in zip(old['teaching_figures'],new['teaching_figures'],strict=True):
        assert all(a[k]==b[k] for k in ('id','source','locator','kind','after'))
    assert '137セッションのうち34では、模擬ユーザーに' in new['sections']['evidence']
    assert '未達とは断定せず' in new['sections']['results']
    assert '24通り' in new['sections']['what_we_verified'] and '6通り' in new['sections']['what_we_verified']
    data_old,data_new=map(json.loads,pair('results.json'))
    for d in (data_old,data_new):
        d.pop('note')
        for frame in d['explorer']['frames']:
            frame.pop('note')
    assert data_old==data_new
    assert len(data_new['explorer']['frames'])==7
    def evaluate(src):
        return ast.dump(next(n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name=='evaluate'))
    a,b=pair('run.py')
    assert evaluate(a)==evaluate(b)

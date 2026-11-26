"""Protect the archived source, formulas, and teaching data after the reading edit."""
import ast
from pathlib import Path
import hashlib
import json
import subprocess

import pytest
import yaml

from prose_preservation import before_assortment_full_prose, assortment_full_prose_hash

ROOT = Path(__file__).resolve().parents[1]
BASE = 'd9c6ed04acd6a741d82bd15baccf6896cc761ab9'
PREFIX = 'papers/assortment-replenishment-hard-constraints'


def historical(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)


def test_exact_archive_and_unchanged_experimental_values():
    rows = json.loads((ROOT / 'tests/assortment_full_prose_hashes.json').read_text())['files']
    names = {'README.md','experiment.md','implementation.md','interactive.html','interactive.js',
             'lab.yaml','mapping.md','method.md','results.json','run.py','validation.md'}
    assert rows.keys() == {f'{PREFIX}/{name}' for name in names}
    for path, row in rows.items():
        raw = (ROOT / path).read_bytes()
        assert raw != historical(path)
        assert before_assortment_full_prose(ROOT, path, raw) == historical(path)
        assert hashlib.sha256(raw).hexdigest() == row['after']['sha256']
        with pytest.raises(AssertionError):
            before_assortment_full_prose(ROOT, path, raw + b'\n')
        for algorithm in ('sha256', 'blob'):
            assert assortment_full_prose_hash(ROOT, path, row['before'][algorithm], algorithm) == row['after'][algorithm]
            with pytest.raises(AssertionError):
                assortment_full_prose_hash(ROOT, path, row['after'][algorithm], algorithm)
    unchanged = f'{PREFIX}/model.js'
    assert (ROOT / unchanged).read_bytes() == historical(unchanged)
    dataset = f'{PREFIX}/results.json'
    a, b = map(json.loads, (historical(dataset), (ROOT / dataset).read_bytes()))
    assert a.pop('note') != b.pop('note')
    assert a == b
    code = f'{PREFIX}/run.py'
    def body(raw):
        tree = ast.parse(raw)
        for n in ast.walk(tree):
            if isinstance(n, ast.keyword) and n.arg == 'note':
                assert isinstance(n.value, ast.Constant)
                n.value = ast.Constant(None)
        return ast.dump(tree)
    assert body(historical(code)) == body((ROOT / code).read_bytes())


def test_formula_data_and_existing_paper_overview_are_unchanged():
    path = f'{PREFIX}/lab.yaml'
    a, b = map(yaml.safe_load, (historical(path), (ROOT / path).read_bytes()))
    editable = {'question','summary','source_review','core_idea','sections','teaching_figures'}
    assert {k:v for k,v in a.items() if k not in editable} == {k:v for k,v in b.items() if k not in editable}
    assert a['sections'].keys() == b['sections'].keys()
    for k in ('overview','method','implementation','mapping','executable_understanding','what_we_verified'):
        assert a['sections'][k] == b['sections'][k]
    assert {k: v for k, v in a['source_review'].items() if k != 'scope'} == {
        k: v for k, v in b['source_review'].items() if k != 'scope'}
    for x, y in zip(a['teaching_figures'], b['teaching_figures'], strict=True):
        for k in ('id','kind','after','source','locator'):
            assert x[k] == y[k]
        for sx, sy in zip(x.get('steps',()), y.get('steps',()), strict=True):
            for k in ('formula','formula_mathml'):
                assert sx[k] == sy[k]

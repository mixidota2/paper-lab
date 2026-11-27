"""Lock the author scope, fallback, and all teaching values while allowing new words."""
import json
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_deletion_prefix_full_prose, deletion_prefix_full_prose_hash

ROOT = Path(__file__).resolve().parents[1]
REL = 'papers/trajectory-deletion-prefix-cost/'


def before(name):
    path = REL + name
    return before_deletion_prefix_full_prose(ROOT, path, (ROOT / path).read_bytes())


def test_exact_bytes_and_wrong_predecessors():
    files = {'README.md','evidence.md','experiment.md','interactive.js','lab.yaml','mapping.md','method.md','render.py','results.json','run.py'}
    rows = json.loads((ROOT / 'tests/deletion_prefix_full_prose_hashes.json').read_text())['files']
    assert set(rows) == {REL + n for n in files}
    for name in files:
        path = REL + name
        raw = (ROOT / path).read_bytes()
        assert before(name) != raw
        row = rows[path]
        for alg in ('sha256', 'blob'):
            assert deletion_prefix_full_prose_hash(ROOT, path, row['before'][alg], alg) == row['after'][alg]
            with pytest.raises(AssertionError):
                deletion_prefix_full_prose_hash(ROOT, path, row['after'][alg], alg)
        with pytest.raises(AssertionError):
            before_deletion_prefix_full_prose(ROOT, path, raw+b'\n')


def test_author_only_overview_and_regenerated_numeric_data():
    after = yaml.safe_load((ROOT / REL / 'lab.yaml').read_bytes())
    prior = yaml.safe_load(before('lab.yaml'))
    for key in ('id','title','authors','year','arxiv_id','urls','status','verification'):
        assert after[key] == prior[key]
    prose = after['sections']['overview']
    assert len(prose.split('\n\n')) == 3
    assert all(x in prose for x in ('9,400回','直近2ターン','5評価','19評価','26評価','費用が下がった評価はなかった'))
    assert all(x not in prose for x in ('Lab','作例','144条件','<table','<figure'))
    a,b = (json.loads(r) for r in ((ROOT / REL / 'results.json').read_bytes(), before('results.json')))
    del a['note'], b['note']
    assert a == b and len(a['synthetic']) == 144
    page = (ROOT / REL / 'experiment.md').read_text()
    assert '<noscript>' in page and '作例の費用単位' in page

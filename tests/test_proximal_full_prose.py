"""Lock the Proximal wording to its numerical evidence and renderer scope."""
import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_proximal_full_prose, proximal_full_prose_hash


ROOT = Path(__file__).resolve().parents[1]
SLUG = 'proximal-residual-value-inventory-placement'
PAPERS = f'papers/{SLUG}'


def test_exact_reversible_prose_and_no_other_renderer_changes():
    rows = json.loads((ROOT / 'tests/proximal_full_prose_hashes.json').read_bytes())['files']
    shared = 'paper_lab/inventory02.py'
    assert set(rows) == {shared, *(f'{PAPERS}/{n}' for n in
                         ('README.md', 'lab.yaml', 'method.md', 'mapping.md', 'results.json', 'run.py'))}
    for path, row in rows.items():
        current = (ROOT / path).read_bytes()
        before = before_proximal_full_prose(ROOT, path, current)
        assert hashlib.sha256(before).hexdigest() == row['before']['sha256']
        for key, digest in (
            ('sha256', hashlib.sha256(current).hexdigest()),
            ('blob', hashlib.sha1(f'blob {len(current)}\0'.encode() + current).hexdigest()),
        ):
            assert proximal_full_prose_hash(ROOT, path, row['before'][key], key) == digest
            with pytest.raises(AssertionError):
                proximal_full_prose_hash(ROOT, path, row['after'][key], key)
        with pytest.raises(AssertionError):
            before_proximal_full_prose(ROOT, path, current + b'\n')
    current = (ROOT / shared).read_bytes()
    before = before_proximal_full_prose(ROOT, shared, current)
    def leave_other_functions(raw):
        pre, rest = raw.split(b'def proximal(r):',1)
        return pre, rest.split(b'def radfl(r):',1)[1]
    assert leave_other_functions(current) == leave_other_functions(before)


def test_numerical_and_source_boundaries():
    path = f'{PAPERS}/lab.yaml'
    current = (ROOT / path).read_bytes()
    old, new = (yaml.safe_load(t) for t in (before_proximal_full_prose(ROOT, path, current),current))
    overview = new['sections']['overview']
    assert old['sections']['overview'] == overview
    assert overview in (ROOT / PAPERS / 'README.md').read_text()
    assert [x['formula'] for x in old['teaching_figures'][0]['steps']] == [
        x['formula'] for x in new['teaching_figures'][0]['steps']]
    path = f'{PAPERS}/results.json'
    current = (ROOT / path).read_bytes()
    old, new = (json.loads(t) for t in (before_proximal_full_prose(ROOT, path, current),current))
    for record in (old,new):
        del record['note']
        for experiment in record['experiments']:
            del experiment['name']
            experiment['metrics'] = list(experiment['metrics'].values())
    assert old == new
    path = f'{PAPERS}/run.py'
    current = (ROOT / path).read_bytes()
    def algorithms(src):
        tree = ast.parse(src)
        return [ast.dump(f) for f in tree.body if isinstance(f,ast.FunctionDef) and f.name in {'allocate','path'}]
    assert algorithms(before_proximal_full_prose(ROOT,path,current)) == algorithms(current)


def test_signed_hessian_example_does_not_require_nonnegative_inverse():
    examples = (
        (((2,1),(1,2)), (F(1,3), F(1,3))),
        (((2,3),(3,5)), (F(2),F(-1))),
    )
    for ((a,b),(c,d)), expected in examples:
        det = a*d-b*c
        inverse = ((F(d,det),F(-b,det)),(F(-c,det),F(a,det)))
        assert inverse[0][1] < 0 and inverse[1][0] < 0
        assert tuple(map(sum,inverse)) == expected
        assert F(1,a) > 0 and F(1,d) > 0

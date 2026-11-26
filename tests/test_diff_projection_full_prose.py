"""Keep the reader-specific rewrite tied to exact prior bytes and calculations."""
import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

import pytest

from prose_preservation import before_diff_projection_full_prose, diff_projection_full_prose_hash


ROOT = Path(__file__).resolve().parents[1]
PAPER = 'papers/diff-projection-feasible-multi-echelon-inventory'


def test_exact_reversible_prose_and_single_renderer_scope():
    rows = json.loads((ROOT / 'tests/diff_projection_full_prose_hashes.json').read_bytes())['files']
    assert set(rows) == {'paper_lab/projection01.py', *(f'{PAPER}/{n}' for n in
                         ('README.md', 'lab.yaml', 'method.md', 'mapping.md', 'results.json', 'run.py'))}
    for path, row in rows.items():
        current = (ROOT / path).read_bytes()
        before = before_diff_projection_full_prose(ROOT, path, current)
        assert hashlib.sha256(before).hexdigest() == row['before']['sha256']
        for key, digest in (
            ('sha256', hashlib.sha256(current).hexdigest()),
            ('blob', hashlib.sha1(f'blob {len(current)}\0'.encode() + current).hexdigest()),
        ):
            assert diff_projection_full_prose_hash(ROOT, path, row['before'][key], key) == digest
            with pytest.raises(AssertionError):
                diff_projection_full_prose_hash(ROOT, path, row['after'][key], key)
        with pytest.raises(AssertionError):
            before_diff_projection_full_prose(ROOT, path, current + b'\n')


def test_data_and_algorithm_are_identical():
    path = f'{PAPER}/results.json'
    current = (ROOT / path).read_bytes()
    old, new = (json.loads(t) for t in (before_diff_projection_full_prose(ROOT, path, current),current))
    assert old.pop('scope') != new.pop('scope')
    assert old == new
    path = f'{PAPER}/run.py'
    current = (ROOT / path).read_bytes()
    def numerical_code(src):
        return [ast.dump(f) for f in ast.parse(src).body if isinstance(f,ast.FunctionDef)
                and f.name in {'project','feasible','objective','integer_map'}]
    assert numerical_code(before_diff_projection_full_prose(ROOT,path,current)) == numerical_code(current)


def test_weighted_capacity_counterexample_does_not_change_toy():
    z = (F(9,10), F(9,5))
    excess = 2*z[0] + z[1] - 3
    continuous = (z[0]-2*excess/5, z[1]-excess/5)
    assert continuous == (F(33,50),F(42,25))
    floor = (0,1)
    assert continuous[1]-floor[1] > continuous[0]-floor[0]
    def objective(q):
        return sum((qi-zi)**2 for qi,zi in zip(q,z))/4
    mapped = (0,2)
    assert objective(mapped) < objective(floor)
    assert 2*(mapped[0]+1)+mapped[1] > 3
    exact = min((objective((a,b)),(a,b)) for a in range(2) for b in range(4-2*a))
    assert objective(mapped) == F(17,80) > exact[0] == F(13,80) and exact[1] == (1,1)

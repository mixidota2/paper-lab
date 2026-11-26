"""Lock RA-DFL's reader-facing revision and independently check its limitations."""
import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_radfl_full_prose, radfl_full_prose_hash


ROOT = Path(__file__).resolve().parents[1]
SLUG = 'ra-dfl-risk-aware-decision-focused-inventory'
PAPERS = f'papers/{SLUG}'


def test_exact_reversible_prose_and_no_other_renderer_changes():
    rows = json.loads((ROOT / 'tests/radfl_full_prose_hashes.json').read_bytes())['files']
    shared = 'paper_lab/inventory02.py'
    assert set(rows) == {shared, *(f'{PAPERS}/{n}' for n in
                         ('README.md', 'lab.yaml', 'method.md', 'mapping.md', 'results.json', 'run.py'))}
    for path, row in rows.items():
        current = (ROOT / path).read_bytes()
        before = before_radfl_full_prose(ROOT, path, current)
        assert hashlib.sha256(before).hexdigest() == row['before']['sha256']
        for key, digest in (
            ('sha256', hashlib.sha256(current).hexdigest()),
            ('blob', hashlib.sha1(f'blob {len(current)}\0'.encode() + current).hexdigest()),
        ):
            assert radfl_full_prose_hash(ROOT, path, row['before'][key], key) == digest
            with pytest.raises(AssertionError):
                radfl_full_prose_hash(ROOT, path, row['after'][key], key)
        with pytest.raises(AssertionError):
            before_radfl_full_prose(ROOT, path, current + b'\n')
    current = (ROOT / shared).read_bytes()
    before = before_radfl_full_prose(ROOT, shared, current)
    def other_functions(raw):
        pre, rest = raw.split(b'def radfl(r):',1)
        return pre, rest.split(b'def widget(result):',1)[1]
    assert other_functions(current) == other_functions(before)


def test_numerical_data_code_and_canonical_overview_unchanged():
    path = f'{PAPERS}/lab.yaml'
    current = (ROOT / path).read_bytes()
    old, new = (yaml.safe_load(t) for t in (before_radfl_full_prose(ROOT, path, current),current))
    assert new['sections']['overview'] == old['sections']['overview']
    assert new['sections']['overview'] in (ROOT / PAPERS / 'README.md').read_text()
    assert [x['formula'] for x in old['teaching_figures'][0]['steps']] == [
        x['formula'] for x in new['teaching_figures'][0]['steps']]
    path = f'{PAPERS}/results.json'
    current = (ROOT / path).read_bytes()
    old, new = (json.loads(t) for t in (before_radfl_full_prose(ROOT, path, current),current))
    for record in (old,new):
        del record['note']
        for experiment in record['experiments']:
            del experiment['name']
            experiment['metrics'] = list(experiment['metrics'].values())
    assert old == new
    assert new['cases'][0]['best']['q'] == [4, 5]
    assert [c['q'] for c in new['cases'][0]['candidates'] if abs(c['mean'] - 9.88) < 1e-9] == [[4,5],[5,4],[6,3]]
    path = f'{PAPERS}/run.py'
    current = (ROOT / path).read_bytes()
    def numeric_code(src):
        tree = ast.parse(src)
        return [ast.dump(f) for f in tree.body if isinstance(f,ast.FunctionDef) and f.name in {'cost','cvar','evaluate'}]
    assert numeric_code(before_radfl_full_prose(ROOT,path,current)) == numeric_code(current)


def test_optional_transfer_cannot_be_justified_by_constant_charge_alone():
    def cost(v, transfer_price):
        return (2-v) + 6*(2-v) + transfer_price*v
    limit = F(4,5)
    assert cost(0,8) == 14 and cost(limit,8) == F(74,5)
    h, b, tau = F(2,100), F(2,100) * F(85,15), F(15,100)
    assert h+b == F(2,15) < tau
    assert h+F(3,2)*b == F(19,100) > tau


def test_lower_bound_does_not_preserve_the_minimal_allocation():
    costs = []
    for qa in range(5):
        for qb in range(5-qa):
            truth = max(qa-3,0)+max(qb-3,0)+6*max(3-qa,0)+2*max(3-qb,0)
            masked = max(qb-3,0)+6*max(1-qa,0)+2*max(3-qb,0)
            costs.append(((qa,qb),truth,masked))
    assert all(masked <= truth for _,truth,masked in costs)
    assert [r for r in costs if r[2]==min(z[2] for z in costs)] == [((1,3),12,0)]
    assert [r for r in costs if r[1]==min(z[1] for z in costs)] == [((3,1),4,4)]

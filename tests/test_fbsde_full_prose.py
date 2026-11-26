"""Keep the FBSDE qualification separate from local QP feasibility."""
import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from paper_lab.fbsde30 import widget
from prose_preservation import before_fbsde_full_prose, fbsde_full_prose_hash


ROOT = Path(__file__).resolve().parents[1]
PAPER = 'papers/constrained-deep-inventory-fbsde'


def test_exact_reversible_prose_for_the_six_downloads_and_renderer():
    rows = json.loads((ROOT / 'tests/fbsde_full_prose_hashes.json').read_bytes())['files']
    assert set(rows) == {'paper_lab/fbsde30.py', *(f'{PAPER}/{n}' for n in
                         ('README.md', 'lab.yaml', 'method.md', 'mapping.md', 'results.json', 'run.py'))}
    for path, row in rows.items():
        current = (ROOT / path).read_bytes()
        before = before_fbsde_full_prose(ROOT, path, current)
        assert hashlib.sha256(before).hexdigest() == row['before']['sha256']
        for key, digest in (
            ('sha256', hashlib.sha256(current).hexdigest()),
            ('blob', hashlib.sha1(f'blob {len(current)}\0'.encode() + current).hexdigest()),
        ):
            assert fbsde_full_prose_hash(ROOT, path, row['before'][key], key) == digest
            with pytest.raises(AssertionError):
                fbsde_full_prose_hash(ROOT, path, row['after'][key], key)
        with pytest.raises(AssertionError):
            before_fbsde_full_prose(ROOT, path, current + b'\n')


def test_data_and_formula_are_identical():
    path = f'{PAPER}/results.json'
    current = (ROOT / path).read_bytes()
    old, new = (json.loads(t) for t in (before_fbsde_full_prose(ROOT, path, current),current))
    for data in (old,new):
        del data['scope'], data['paper_reported']['source']
        for frame in data['frames']:
            del frame['label']
    assert old == new

    path = f'{PAPER}/run.py'
    current = (ROOT / path).read_bytes()
    def numerical_frame(src):
        tree = ast.parse(src)
        frame = next(f for f in tree.body if isinstance(f, ast.FunctionDef) and f.name == 'frame')
        ret = next(statement for statement in frame.body if isinstance(statement, ast.Return))
        ret.value.keywords = [k for k in ret.value.keywords if k.arg != 'label']
        return ast.dump(frame)
    assert numerical_frame(before_fbsde_full_prose(ROOT,path,current)) == numerical_frame(current)

    path = f'{PAPER}/lab.yaml'
    current = (ROOT / path).read_bytes()
    old, new = (yaml.safe_load(t) for t in (before_fbsde_full_prose(ROOT, path, current),current))
    assert old['sections']['overview'] == new['sections']['overview']
    assert new['sections']['overview'] in (ROOT / PAPER / 'README.md').read_text()
    assert [x['formula'] for x in old['teaching_figures'][0]['steps']] == [
        x['formula'] for x in new['teaching_figures'][0]['steps']]


def test_h8_has_a_local_solution_without_meeting_the_start_condition():
    data = json.loads((ROOT / PAPER / 'results.json').read_bytes())
    for f in data['frames']:
        H = F(f['capacity'])
        upper = min(3, (H-7)/2)
        assert f['h1'] == (H-9)/2
        assert f['order'] == (None if upper < 0 else min(4, upper))
    h8 = next(f for f in data['frames'] if f['capacity'] == 8)
    assert h8['feasible'] and h8['order'] == .5 and not h8['augmented_initial_safe']
    html = widget(data)
    raw = html.split('data-frames>',1)[1].split('</script>',1)[0]
    frames = json.loads(raw)
    assert '発注率 0.5' in frames[1] and 'その後に必ず容量を超えるという意味ではありません' in frames[1]
    assert '非負の発注率はありません' in frames[0]
    assert '発注率 1.5' in frames[2] and '発注率 3' in frames[3]

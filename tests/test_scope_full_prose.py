"""Keep the SCOPE rewrite tied to the old numerical experiment and archived prose."""
import ast
import hashlib
import json
import re
from fractions import Fraction as F
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_reasoncast_all_full_prose, before_onetrans_full_prose, before_eval_grain_full_prose, before_scope_full_prose, scope_full_prose_hash


ROOT = Path(__file__).resolve().parents[1]
PAPER = 'papers/scope-coupled-supply-chain-policies'
RENDERER = 'paper_lab/batch28.py'


def test_exact_archives_and_untouched_renderer_branches():
    rows = json.loads((ROOT / 'tests/scope_full_prose_hashes.json').read_bytes())['files']
    assert set(rows) == {RENDERER, *(f'{PAPER}/{n}' for n in
                         ('README.md', 'lab.yaml', 'method.md', 'mapping.md', 'results.json', 'run.py'))}
    for path, row in rows.items():
        current = before_eval_grain_full_prose(ROOT, path, before_onetrans_full_prose(ROOT, path, before_reasoncast_all_full_prose(ROOT,path,(ROOT / path).read_bytes())))
        before = before_scope_full_prose(ROOT, path, current)
        assert hashlib.sha256(before).hexdigest() == row['before']['sha256']
        for key, digest in (
            ('sha256', hashlib.sha256(current).hexdigest()),
            ('blob', hashlib.sha1(f'blob {len(current)}\0'.encode() + current).hexdigest()),
        ):
            assert scope_full_prose_hash(ROOT, path, row['before'][key], key) == digest
            with pytest.raises(AssertionError):
                scope_full_prose_hash(ROOT, path, row['after'][key], key)
        with pytest.raises(AssertionError):
            before_scope_full_prose(ROOT, path, current + b'\n')

    current = before_eval_grain_full_prose(ROOT, RENDERER, before_onetrans_full_prose(ROOT, RENDERER, before_reasoncast_all_full_prose(ROOT,RENDERER,(ROOT / RENDERER).read_bytes())))
    old = before_scope_full_prose(ROOT, RENDERER, current)
    def other_branches(src):
        before, rest = src.split(b"        elif kind=='scope':",1)
        _, after = rest.split(b"        elif kind=='onetrans':",1)
        after = re.sub(rb"'scope':'[^']+'",b"'scope':<copy>",after,count=1)
        return before,after.split(b'    return ',1)[0].split(b"    label=",1)[0]
    assert other_branches(current) == other_branches(old)


def test_old_numbers_and_original_paper_overview_remain_exact():
    path = f'{PAPER}/results.json'
    current = (ROOT / path).read_bytes()
    old, new = (json.loads(t) for t in (before_scope_full_prose(ROOT, path, current),current))
    for obj in (old,new):
        del obj['note']
        for frame in obj['frames']:
            del frame['label']
    assert new == old
    assert [(x['dispatch'], x['proposed']['item'], x['proposed']['cycle']) for x in new['frames']] == [
        (0,'A',1),(2,'A',2),(10,'B',2),(30,'B',2)]
    path = f'{PAPER}/run.py'
    current = (ROOT / path).read_bytes()
    before = before_scope_full_prose(ROOT,path,current)
    def numerical_function(src):
        return ast.dump(next(node for node in ast.parse(src).body if isinstance(node,ast.FunctionDef)
                             and node.name=='utility'))
    assert numerical_function(before) == numerical_function(current)
    path = f'{PAPER}/lab.yaml'
    current = (ROOT / path).read_bytes()
    old, new = (yaml.safe_load(t) for t in (before_scope_full_prose(ROOT, path, current),current))
    assert new['sections']['overview'] == old['sections']['overview']
    assert new['sections']['overview'] in (ROOT / PAPER / 'README.md').read_text()


def test_offline_evidence_and_two_daily_comparators_are_not_conflated():
    lab = yaml.safe_load((ROOT / PAPER / 'lab.yaml').read_bytes())
    ev = lab['sections']['evidence']
    assert '参照値で調整した日次の指標' in ev and '通貨で測った実現利益' in ev
    assert all(s in ev for s in ('53.65', '約0.026%', '表2でSCOPEの補充を毎日に固定', '279,026.38',
                                 '表1で毎日補充する比較手法の最高値283,074.28'))
    assert round(float(100*F('53.65')/F('206276.14')),3) == .026
    method = (ROOT / PAPER / 'method.md').read_text()
    assert 'グループ別に間隔を変えたときの正解は作りません' in method
    assert '検証の評価値を各段階へ勾配として戻すわけではありません' in method

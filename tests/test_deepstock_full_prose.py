"""Preserve archived DeepStock source and public distinctions between studies."""
import json
from pathlib import Path
import subprocess

import pytest
import yaml

from prose_preservation import before_deepstock_full_prose, deepstock_full_prose_hash

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'deepstock-policy-regularized-inventory-drl'
FOLDER = f'papers/{SLUG}'
BASE = 'c2e4172a0f3e7ab083dcfee9be7619575074a0dd'


def previous(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)


def test_deepstock_keeps_a_strict_reversible_source_record():
    records = json.loads((ROOT / 'tests/deepstock_full_prose_hashes.json').read_text())['files']
    touched = {'README.md', 'lab.yaml', 'mapping.md', 'method.md', 'results.json', 'run.py'}
    assert records.keys() == {f'{FOLDER}/{item}' for item in touched} | {'paper_lab/deepstock01.py'}
    for p, h in records.items():
        now = (ROOT / p).read_bytes()
        original = previous(p)
        assert now != original
        assert before_deepstock_full_prose(ROOT, p, now) == original
        for method in ('sha256', 'blob'):
            assert deepstock_full_prose_hash(ROOT, p, h['before'][method], method) == h['after'][method]
            with pytest.raises(AssertionError):
                deepstock_full_prose_hash(ROOT, p, h['after'][method], method)
        with pytest.raises(AssertionError):
            before_deepstock_full_prose(ROOT, p, now + b'\n')


def test_deepstock_april_does_not_export_an_invented_zero_stockout_difference():
    y = f'{FOLDER}/lab.yaml'
    before, after = [yaml.safe_load(s) for s in (previous(y), (ROOT / y).read_bytes())]
    assert before['sections']['overview'] == after['sections']['overview']
    r = f'{FOLDER}/results.json'
    base, now = [json.loads(s) for s in (previous(r), (ROOT / r).read_bytes())]
    for key in ('checks', 'frames', 'offline', 'turnover_by_class', 'verification'):
        assert base[key] == now[key]
    assert [i['tt_days'] for i in now['deployment']] == [-9.53, -1, -2]
    for row in now['deployment'][1:]:
        assert row['sr_pp'] is None and row['sr_reported_percent'] is None
        assert row['sr_status'] == 'no_distinguishable_difference'
    jul = now['deployment'][0]
    assert jul['sr_pp'] is None and jul['sr_reported_percent'] == -0.83
    assert jul['sr_status'] == 'reported_as_percent'

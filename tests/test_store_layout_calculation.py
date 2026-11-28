import hashlib
import json
from pathlib import Path
from prose_preservation import historical_lab_public_guide
import runpy

import pytest

from prose_preservation import before_store_layout_calculation

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / 'guides/store-layout-fixed-counts.md'
FIXTURE = ROOT / 'tests/fixtures/store-layout-fixed-counts-results.json'


def test_fixed_counts_and_connectivity_exact_example():
    code = runpy.run_path(ROOT / 'tools/store_layout_fixed_counts_example.py')
    actual = code['run']()
    assert json.dumps(actual, indent=2) + '\n' == FIXTURE.read_text()
    assert actual['layouts_with_counts'] == 27720
    assert actual['layouts_connected_no_aisle_crossing'] == 16
    cases = actual['cases']
    for name, a in cases.items():
        assert a['counts_ok']
        assert a['connected_no_aisle_crossing'] == (name not in ('greedy', 'counts_only'))
        assert a['position'] + a['pair'] == a['total']
    assert cases['counts_only']['position'] == 97
    assert cases['connected_additive']['position'] == 91
    assert cases['connected_with_pairs']['total'] == 124
    assert cases['swap_from_current']['total'] == 108
    assert cases['swap_from_second_start']['total'] == 124


def test_calculation_edit_preserves_prior_guide_and_numeric_copy():
    raw = historical_lab_public_guide(ROOT,str(GUIDE.relative_to(ROOT)))
    old = before_store_layout_calculation(ROOT, raw)
    row = json.loads((ROOT / 'tests/store_layout_calculation_hashes.json').read_text())
    assert hashlib.sha256(old).hexdigest() == row['before_sha256']
    with pytest.raises(AssertionError):
        before_store_layout_calculation(ROOT, raw + b'\n')
    section = row['section']
    for exact in ('27,720通り', '16通り', '97点から91点', '123点から124点',
                  '「AAAC / AABC / BBBC」から「AAAC / ABAC / BBBC」',
                  '124点には16点届かない', '売上や粗利ではない'):
        assert exact in section

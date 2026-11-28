"""Pin the stockout example without accepting any other guide edits."""
import hashlib
import json
from pathlib import Path
from prose_preservation import historical_lab_public_guide
import re

import pytest

from prose_preservation import before_stockout_example, stockout_example_hash

ROOT = Path(__file__).resolve().parents[1]
GUIDE = 'guides/forecast-to-replenishment.md'


def hashes(data):
    return {
        'sha256': hashlib.sha256(data).hexdigest(),
        'blob': hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest(),
    }


def test_stockout_is_one_exact_insertion_after_axial():
    current = historical_lab_public_guide(ROOT,GUIDE)
    row = json.loads((ROOT / 'tests/replenishment_stockout_hashes.json').read_text())
    axial = json.loads((ROOT / 'tests/replenishment_axial_hashes.json').read_text())
    block = row['inserted'].encode()
    previous = before_stockout_example(ROOT, GUIDE, current)
    assert hashes(current) == row['after']
    assert hashes(previous) == row['before'] == axial['after']
    assert current.count(block) == 1 and block not in previous
    assert current.replace(block, b'', 1) == previous
    assert current.count(b'<!-- EVIDENCE_CARDS -->') == previous.count(b'<!-- EVIDENCE_CARDS -->') == 1
    for algorithm in row['after']:
        assert stockout_example_hash(ROOT, GUIDE, row['before'][algorithm], algorithm) == row['after'][algorithm]
        for invalid in (row['after'][algorithm], '0' * len(row['after'][algorithm])):
            with pytest.raises(AssertionError):
                stockout_example_hash(ROOT, GUIDE, invalid, algorithm)
    for invalid in (previous, current + b'\n', current.replace(block, block * 2, 1),
                    current.replace(block, block.replace(b'600', b'601'), 1)):
        with pytest.raises(AssertionError):
            before_stockout_example(ROOT, GUIDE, invalid)


def test_stockout_example_reverses_the_order_preference_under_same_sales_log():
    row = json.loads((ROOT / 'tests/replenishment_stockout_hashes.json').read_text())
    expected = [
        (demand, *(150 * min(quantity, demand) - 100 * max(quantity - demand, 0)
                   for quantity in (2, 4)))
        for demand in (2, 4)
    ]
    cells = [tuple(map(int, cols)) for cols in
             re.findall(r'^\| (\d+)個 \| (\d+)円 \| (\d+)円 \|$', row['inserted'], re.MULTILINE)]
    assert cells == expected == [(2, 300, 100), (4, 300, 600)]
    assert min(2, expected[0][0]) == min(2, expected[1][0]) == 2
    assert cells[0][1] > cells[0][2] and cells[1][1] < cells[1][2]

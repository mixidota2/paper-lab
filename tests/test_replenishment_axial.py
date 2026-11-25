"""Pin the scope of the operational example without relaxing older guide guards."""
import hashlib
import json
from pathlib import Path
import re

import pytest

from prose_preservation import axial_ingredient_order_hash, before_axial_ingredient_order, before_weather_cutoff

ROOT = Path(__file__).resolve().parents[1]
GUIDE = 'guides/forecast-to-replenishment.md'


def hashes(data):
    return {
        'sha256': hashlib.sha256(data).hexdigest(),
        'blob': hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest(),
    }


def test_axial_is_one_exact_insertion_after_the_prior_revision():
    current = (ROOT/GUIDE).read_bytes()
    receipt = json.loads((ROOT/'tests/replenishment_axial_hashes.json').read_text())
    weather = json.loads((ROOT/'tests/replenishment_weather_cutoff_hashes.json').read_text())
    block = receipt['inserted'].encode()
    prior = before_axial_ingredient_order(ROOT, GUIDE, current)
    assert hashes(current) == receipt['after']
    assert hashes(prior) == receipt['before'] == weather['after']
    assert hashes(before_weather_cutoff(ROOT, GUIDE, current)) == weather['before']
    assert current.count(block) == 1 and block not in prior
    assert current.replace(block, b'', 1) == prior
    assert current.count(b'<!-- EVIDENCE_CARDS -->') == prior.count(b'<!-- EVIDENCE_CARDS -->') == 1
    assert [x.decode() for x in re.findall(rb'\]\((https?://[^)]+)\)', block)] == [
        'https://tdnet-pdf.kabutan.jp/20261026/140120261023555561.pdf#page=32']
    for phrase in ('架空の例', '報告書には導入店数や改善幅、具体的な発注ルールの記載がない',
                   '原料の自動発注に生成AIを使っているかは分からない',
                   '6.0 kg', '2.8 kg', '2ケース（4 kg）', '1.2 kg'):
        assert phrase.encode() in block
    for algo in receipt['after']:
        assert axial_ingredient_order_hash(ROOT, GUIDE, receipt['before'][algo], algo) == receipt['after'][algo]
        for invalid in (receipt['after'][algo], '0'*len(receipt['after'][algo])):
            with pytest.raises(AssertionError):
                axial_ingredient_order_hash(ROOT, GUIDE, invalid, algo)
    for invalid in (prior, current+b'\n', current.replace(block, block*2, 1),
                    current.replace('架空の例'.encode(), '実測した例'.encode(), 1)):
        with pytest.raises(AssertionError):
            before_axial_ingredient_order(ROOT, GUIDE, invalid)

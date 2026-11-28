import hashlib
import json
from pathlib import Path
from prose_preservation import historical_lab_public_guide

import pytest

from prose_preservation import (
    before_store_layout_calculation,
    store_layout_field_example_hash,
    store_layout_full_rewrite_hash,
    store_layout_normandy_hash,
)


ROOT = Path(__file__).resolve().parents[1]
GUIDE = 'guides/store-layout-fixed-counts.md'


def test_normandy_chain_rejects_unreviewed_state():
    original = json.loads((ROOT / 'tests/store_layout_full_rewrite_hashes.json').read_text())['files'][GUIDE]
    extra = json.loads((ROOT / 'tests/store_layout_normandy_hashes.json').read_text())['files'][GUIDE]
    assert extra['before_sha256'] == original['after_sha256']
    assert extra['before_blob'] == original['after_blob']
    field = json.loads((ROOT / 'tests/store_layout_field_example_hashes.json').read_text())['files'][GUIDE]
    raw = historical_lab_public_guide(ROOT,GUIDE)
    git_blob = hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
    for algo, value in [('sha256', hashlib.sha256(raw).hexdigest()), ('blob', git_blob)]:
        assert store_layout_full_rewrite_hash(ROOT, GUIDE, original['before_' + algo], algo) == value
        assert store_layout_normandy_hash(ROOT, GUIDE, extra['before_' + algo], algo) == value
        assert field['before_' + algo] == extra['after_' + algo]
        assert store_layout_field_example_hash(ROOT, GUIDE, field['before_' + algo], algo) == value
        with pytest.raises(AssertionError):
            store_layout_normandy_hash(ROOT, GUIDE, value, algo)
        with pytest.raises(AssertionError):
            store_layout_field_example_hash(ROOT, GUIDE, value, algo)


def test_store_timing_example_leaves_previously_reviewed_guide_byte_identical():
    receipt = json.loads((ROOT / 'tests/store_layout_field_example_hashes.json').read_text())['files'][GUIDE]
    raw = before_store_layout_calculation(ROOT, historical_lab_public_guide(ROOT,GUIDE))
    opening = '### 棚を動かした日時と、売上を集計する日をそろえる\n'.encode()
    closing = '5・4・3本の図は'.encode()
    assert raw.count(opening) == raw.count(closing) == 1
    first, last = raw.index(opening), raw.index(closing)
    assert first < last
    assert hashlib.sha256(raw[first:last]).hexdigest() == receipt['section_sha256']
    assert hashlib.sha256(raw[:first] + raw[last:]).hexdigest() == receipt['before_sha256']


def test_normandy_in_context_is_an_estimate_for_one_layout():
    text = (ROOT / GUIDE).read_text()
    section = text.split('### Ben Abdelazizほか：衝動買いによる利益と歩行の推計\n', 1)[1].split('\n### ', 1)[0]
    for expected in (
        '当時の配置に比べ', '衝動買いによる利益が82%増え', '歩行を表す指標が11%下がる',
        'モデルで求めた推計', '配置を変えた後の実測値ではない', '歩行指標の定義や単位',
    ):
        assert expected in section
    assert 'program_euro32.pdf' in text

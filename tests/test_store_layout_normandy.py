import hashlib
import json
from pathlib import Path

import pytest

from prose_preservation import store_layout_full_rewrite_hash, store_layout_normandy_hash


ROOT = Path(__file__).resolve().parents[1]
GUIDE = 'guides/store-layout-fixed-counts.md'


def test_normandy_chain_rejects_unreviewed_state():
    original = json.loads((ROOT / 'tests/store_layout_full_rewrite_hashes.json').read_text())['files'][GUIDE]
    extra = json.loads((ROOT / 'tests/store_layout_normandy_hashes.json').read_text())['files'][GUIDE]
    assert extra['before_sha256'] == original['after_sha256']
    assert extra['before_blob'] == original['after_blob']
    raw = (ROOT / GUIDE).read_bytes()
    git_blob = hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
    for algo, value in [('sha256', hashlib.sha256(raw).hexdigest()), ('blob', git_blob)]:
        assert store_layout_full_rewrite_hash(ROOT, GUIDE, original['before_' + algo], algo) == value
        assert store_layout_normandy_hash(ROOT, GUIDE, extra['before_' + algo], algo) == value
        with pytest.raises(AssertionError):
            store_layout_normandy_hash(ROOT, GUIDE, value, algo)


def test_normandy_in_context_is_an_estimate_for_one_layout():
    text = (ROOT / GUIDE).read_text()
    section = text.split('### Ben Abdelazizほか：衝動買いによる利益と歩行の推計\n', 1)[1].split('\n### ', 1)[0]
    for expected in (
        '当時の配置に比べ', '衝動買いによる利益が82%増え', '歩行を表す指標が11%下がる',
        'モデルで求めた推計', '配置を変えた後の実測値ではない', '歩行指標の定義や単位',
    ):
        assert expected in section
    assert 'program_euro32.pdf' in text

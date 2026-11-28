import hashlib
import json
from pathlib import Path

import pytest
from prose_preservation import before_bridging_reader_full_prose, bridging_full_rewrite_hash, paper_overview_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]


def test_bridging_full_rewrite_is_exact_and_rejects_unknown_versions():
    stem = 'papers/bridging-forecast-accuracy-inventory-kpis/'
    rows = json.loads((ROOT / 'tests/bridging_full_rewrite_hashes.json').read_text())['files']
    assert set(rows) == {stem + x for x in ['README.md', 'lab.yaml', 'method.md', 'mapping.md']} | {'paper_lab/forecast01.py'}
    for path, row in rows.items():
        body = before_bridging_reader_full_prose(ROOT, path, (ROOT / path).read_bytes())
        assert paper_overview_rewrite_hash(ROOT, path, bridging_full_rewrite_hash(ROOT, path, row['before_sha256']), 'sha256') == hashlib.sha256(body).hexdigest()
        assert paper_overview_rewrite_hash(ROOT, path, bridging_full_rewrite_hash(ROOT, path, row['before_blob'], 'blob'), 'blob') == hashlib.sha1(f'blob {len(body)}\0'.encode()+body).hexdigest()
        with pytest.raises(AssertionError):
            bridging_full_rewrite_hash(ROOT, path, '0' * 64)
    assert bridging_full_rewrite_hash(ROOT, stem + 'run.py', 'preserve') == 'preserve'

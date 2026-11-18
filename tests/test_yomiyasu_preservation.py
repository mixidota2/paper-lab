"""Exact November identities and rejection of unreviewed bytes."""
import hashlib
import json
from pathlib import Path
import pytest
from prose_preservation import yomiyasu_hash, before_yomiyasu_replenishment, issue21_hash
ROOT = Path(__file__).resolve().parents[1]


def test_reviewed_final_files_and_wrong_prior_hashes():
    rows = json.loads((ROOT / 'tests/yomiyasu_revision_hashes.json').read_text())['files']
    for path, row in rows.items():
        data = (ROOT / path).read_bytes()
        assert hashlib.sha256(data).hexdigest() == issue21_hash(ROOT, path, row['after_sha256']), path
        assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == issue21_hash(ROOT, path, row['after_blob'], 'blob'), path
        for algorithm in ('sha256', 'blob'):
            assert yomiyasu_hash(ROOT, path, row['before_' + algorithm], algorithm) == issue21_hash(ROOT, path, row['after_' + algorithm], algorithm)
            with pytest.raises(AssertionError):
                yomiyasu_hash(ROOT, path, 'unreviewed', algorithm)


def test_replenishment_reverse_rejects_unrelated_mutation():
    path = 'papers/assortment-replenishment-hard-constraints/interactive.js'
    data = (ROOT / path).read_text()
    assert before_yomiyasu_replenishment(ROOT, path, data) != data
    with pytest.raises(AssertionError):
        before_yomiyasu_replenishment(ROOT, path, data + '\n')

"""The later prose review preserves earlier hashes and rejects unknown bytes."""
import hashlib
import json
from pathlib import Path

import pytest

from prose_preservation import issue21_hash, reading_prose_hash, yomiyasu_hash

ROOT = Path(__file__).resolve().parents[1]


def test_reading_revision_final_files_preserve_exact_previous_identities():
    rows = json.loads((ROOT / 'tests/reading_prose_revision_hashes.json').read_text())['files']
    prior = json.loads((ROOT / 'tests/yomiyasu_revision_hashes.json').read_text())['files']
    issue21 = json.loads((ROOT / 'tests/issue21_revision_hashes.json').read_text())['files']
    for path, row in rows.items():
        content = (ROOT / path).read_bytes()
        actual = {
            'sha256': hashlib.sha256(content).hexdigest(),
            'blob': hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest(),
        }
        for alg, digest in actual.items():
            old = row['before_' + alg]
            assert reading_prose_hash(ROOT, path, old, alg) == digest, path
            preceding = old
            if path in issue21:
                assert old == issue21[path]['after_' + alg], path
                preceding = issue21[path]['before_' + alg]
                with pytest.raises(AssertionError):
                    issue21_hash(ROOT, path, old, alg)
            assert issue21_hash(ROOT, path, preceding, alg) == digest, path
            if path in prior:
                assert preceding == prior[path]['after_' + alg], path
                assert yomiyasu_hash(ROOT, path, prior[path]['before_' + alg], alg) == digest
            for wrong in ('0' * len(old), digest):
                with pytest.raises(AssertionError):
                    reading_prose_hash(ROOT, path, wrong, alg)

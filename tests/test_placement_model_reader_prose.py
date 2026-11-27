import hashlib
import json

import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def before_placement_model_reader_prose(root,raw):
    path = 'papers/shelf-placement-options/model.js'
    entries = json.loads((root/'tests/placement_model_full_prose_hashes.json').read_text())['files']
    assert set(entries) == {path}
    info = entries[path]
    assert hashlib.sha256(raw).hexdigest() == info['after_sha256']
    lines = raw.decode().splitlines()
    assert [line for line in lines if line.startswith('// ')] == info['new_comments']
    without_comments = '\n'.join(line for line in lines if not line.startswith('// ')) + '\n'
    assert without_comments.count(info['new_error']) == 1
    restored_code = without_comments.replace(info['new_error'], info['old_error'])
    assert hashlib.sha256(restored_code.encode()).hexdigest() == info['code_without_comments_and_with_old_error_sha256']
    before = restored_code.splitlines()
    before[2:2] = info['original_comments']
    prior = ('\n'.join(before) + '\n').encode()
    assert hashlib.sha256(prior).hexdigest() == info['before_sha256']
    return prior


def test_placement_model_keeps_arithmetic_and_result_ids_exact():
    path = 'papers/shelf-placement-options/model.js'
    current = (ROOT/path).read_bytes()
    prior = before_placement_model_reader_prose(ROOT,current)
    assert prior != current
    with pytest.raises(AssertionError):
        before_placement_model_reader_prose(ROOT,current+b'\n')

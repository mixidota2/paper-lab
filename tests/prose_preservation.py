"""Translate only exact old identities of the listed prose revisions."""
import json


def revised_hash(root, path, expected, algorithm='sha256'):
    revisions = json.loads((root / 'tests/prose_revision_hashes.json').read_text())['files']
    if path not in revisions:
        return expected
    row = revisions[path]
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]

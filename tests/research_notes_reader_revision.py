"""Preserve the prior reviewed copies of two reader-facing research notes."""

import hashlib
import json

README = 'research-data/README.md'
SHELF = 'research-data/shelf/shelf-allocation-evidence-2026-10-29.md'


def identity(data, algorithm):
    if algorithm == 'sha256':
        return hashlib.sha256(data).hexdigest()
    assert algorithm == 'blob'
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def revisions(root):
    return json.loads((root / 'tests/research_notes_reader_revision.json').read_text())


def research_notes_reader_hash(root, path, expected, algorithm='sha256'):
    if path not in {README, SHELF}:
        return expected
    row = revisions(root)[path]
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_research_notes_reader(root, path, current):
    row = revisions(root)[path]
    assert identity(current, 'sha256') == row['after']['sha256'], path
    new = row['new'].encode()
    assert current.count(new) == 1, path
    prior = current.replace(new, row['old'].encode())
    assert identity(prior, 'sha256') == row['before']['sha256'], path
    return prior

"""Exact source-level preservation for the HASTERAD and ORPR corrections."""

import hashlib
import json
import re

from research_notes_reader_revision import research_notes_reader_hash

HASTERAD = 'papers/hasterad-retail-substitution/lab.yaml'
ORPR_ARCHIVE = 'research-data/README.md'
OVERVIEW = rb'^  overview: [^\n]+\n(?:    [^\n]+\n|\n(?=    [^\n]+\n))*'


def source_overview_correction_hash(root, path, expected, algorithm='sha256'):
    if path not in {HASTERAD, ORPR_ARCHIVE}:
        return expected
    row = _receipt(root)['files'][path]
    assert expected == row['before'][algorithm], path
    if path == ORPR_ARCHIVE:
        return research_notes_reader_hash(root, path, row['after'][algorithm], algorithm)
    return row['after'][algorithm]


def before_hasterad_overview_correction(root, path, current):
    if path != HASTERAD:
        return current
    receipt = _receipt(root)
    row = receipt['files'][path]
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    matches = list(re.finditer(OVERVIEW, current, re.M))
    assert len(matches) == 1, path
    field = matches[0]
    prior = current[:field.start()] + receipt['prior_overview_field'].encode() + current[field.end():]
    assert hashlib.sha256(prior).hexdigest() == row['before']['sha256'], path
    return prior


def _receipt(root):
    return json.loads((root / 'tests/source_overview_corrections.json').read_text())

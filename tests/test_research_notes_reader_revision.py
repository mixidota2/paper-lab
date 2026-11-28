"""The two revised sentences preserve historical readings and links exactly."""

import json
import re
from pathlib import Path

import pytest

from prose_preservation import reading_prose_hash
from research_notes_reader_revision import (
    README, SHELF, before_research_notes_reader, identity, research_notes_reader_hash, revisions,
)
from source_overview_corrections import source_overview_correction_hash

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('path', [README, SHELF])
def test_exact_revision_preserves_one_sentence_and_all_references(path):
    rows = revisions(ROOT)
    assert rows.keys() == {README, SHELF}
    row = rows[path]
    current = (ROOT / path).read_bytes()
    before = before_research_notes_reader(ROOT, path, current)
    assert before.count(row['old'].encode()) == 1
    assert before.replace(row['old'].encode(), row['new'].encode()) == current
    for pattern in (rb'^#.*$', rb'\[[^\]]+\]\([^)]+\)', rb'<a id="[^"]+">', rb'\d+(?:\.\d+)?', rb'\|'):
        assert re.findall(pattern, before, re.M) == re.findall(pattern, current, re.M)
    with pytest.raises(AssertionError):
        before_research_notes_reader(ROOT, path, current + b'\n')


@pytest.mark.parametrize('path', [README, SHELF])
@pytest.mark.parametrize('algorithm', ['sha256', 'blob'])
def test_historical_layer_also_reaches_the_current_bytes(path, algorithm):
    row = revisions(ROOT)[path]
    current = identity((ROOT / path).read_bytes(), algorithm)
    assert research_notes_reader_hash(ROOT, path, row['before'][algorithm], algorithm) == current
    if path == README:
        historical = json.loads((ROOT / 'tests/source_overview_corrections.json').read_text())['files'][path]
        assert historical['after'][algorithm] == row['before'][algorithm]
        assert source_overview_correction_hash(ROOT, path, historical['before'][algorithm], algorithm) == current
    else:
        historical = json.loads((ROOT / 'tests/reading_prose_revision_hashes.json').read_text())['files'][path]
        assert historical['after_' + algorithm] == row['before'][algorithm]
        assert reading_prose_hash(ROOT, path, historical['before_' + algorithm], algorithm) == current
    for unexpected in (current, '0' * len(current)):
        with pytest.raises(AssertionError):
            research_notes_reader_hash(ROOT, path, unexpected, algorithm)


def test_dated_research_questions_remain_a_verbatim_record():
    record = (ROOT / 'research-data/research-questions-2026-10-08.md').read_bytes()
    assert identity(record, 'sha256') == 'e342854f153ac7bee41dc5dc7af16262b91fba611aa995b0e3c87cc521c40d66'

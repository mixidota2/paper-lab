"""Pinned main catalog: adding WRAPPED must retain every existing Lab."""
import json
from pathlib import Path

WRAPPED = 'wrapped-produce-placement-controlled-trial'
BASE = json.loads(Path(__file__).with_name('main_103_catalog.json').read_text())
EXISTING = frozenset(BASE['ids'])
assert BASE['base'] == '0c5d1f13367fbca22a72c12ae172f97c54098920'
assert len(BASE['ids']) == len(EXISTING) == 103
assert WRAPPED not in EXISTING


def assert_catalog(ids):
    actual = list(ids)
    assert len(actual) == len(set(actual)) == 104
    assert set(actual) == EXISTING | {WRAPPED}, 'Existing main Labs must remain; only WRAPPED is added'

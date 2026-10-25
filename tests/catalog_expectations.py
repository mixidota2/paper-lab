"""Pinned main catalog: adding TRACE must retain every existing Lab."""
import json
from pathlib import Path

WRAPPED = 'wrapped-produce-placement-controlled-trial'
TRACE = 'trace-verifier-brittleness'
BASE = json.loads(Path(__file__).with_name('main_104_catalog.json').read_text())
EXISTING = frozenset(BASE['ids'])
assert BASE['base'] == '38e98ef18dde9a88c14cd12a79827084187eff6c'
assert len(BASE['ids']) == len(EXISTING) == 104
assert WRAPPED in EXISTING
assert TRACE not in EXISTING


def assert_catalog(ids):
    actual = list(ids)
    assert len(actual) == len(set(actual)) == 105
    assert set(actual) == EXISTING | {TRACE}, 'Existing main Labs must remain; only TRACE is added'

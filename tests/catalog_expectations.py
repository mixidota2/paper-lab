"""Pinned main catalog: adding EpiSEM must retain every existing Lab."""
import json
from pathlib import Path

WRAPPED = 'wrapped-produce-placement-controlled-trial'
FEATUREARC = 'featurearc-inherited-defects-chain-gates'
DELETION = 'trajectory-deletion-prefix-cost'
TRACE = 'trace-verifier-brittleness'
EPISEM = 'episem-missing-evidence-recovery'
CURRENT = json.loads(Path(__file__).with_name('main_105_catalog.json').read_text())
assert CURRENT['base'] == 'b249cf98c1460c08ed584cba9900fb0aa0815646'
assert len(CURRENT['ids']) == len(set(CURRENT['ids'])) == 105
BASE = json.loads(Path(__file__).with_name('main_104_catalog.json').read_text())
EXISTING = frozenset(BASE['ids'])
assert BASE['base'] == '38e98ef18dde9a88c14cd12a79827084187eff6c'
assert len(BASE['ids']) == len(EXISTING) == 104
assert WRAPPED in EXISTING
assert TRACE not in EXISTING


def assert_catalog(ids):
    actual = list(ids)
    assert len(actual) == len(set(actual)) == 108
    assert set(CURRENT['ids']) == EXISTING | {TRACE}
    assert set(actual) == set(CURRENT['ids']) | {EPISEM, DELETION, FEATUREARC}, 'Existing main Labs must remain; EpiSEM and deletion-cost Labs coexist'

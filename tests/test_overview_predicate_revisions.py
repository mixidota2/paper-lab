"""The rendered overview and its mirror preserve the exact paper evidence."""
from hashlib import sha1, sha256
import json
from pathlib import Path
import re

import pytest
import yaml

from overview_predicate_revisions import (
    PREFIXES, before_overview_predicate_revision, overview_predicate_hash,
)

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_NUMBERS = {
    'invevolve-whitebox-inventory-evolution': {'30', '25', '13', '20'},
    'pilot-experiment-lifecycle': {'1.00%', '1.40%', '53.3%', '93.3%'},
    'oxygenrec-v2-idgr': {'6', '1.61', '4.44%', '4.25%'},
}

@pytest.mark.parametrize('path', [p+n for p in PREFIXES for n in ('README.md', 'lab.yaml')])
def test_previous_text_is_recoverable_and_no_other_bytes_changed(path):
    current = (ROOT/path).read_bytes()
    old = before_overview_predicate_revision(ROOT, path, current)
    manifest = json.loads((ROOT/'tests/overview_predicate_revisions.json').read_text())
    assert set(manifest) == {p+n for p in PREFIXES for n in ('README.md', 'lab.yaml')}
    row = manifest[path]
    assert old.replace(row['old'].encode(), row['new'].encode(), 1) == current

    def identities(raw):
        return {
            'sha256': sha256(raw).hexdigest(),
            'blob': sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest(),
        }
    assert identities(old) == row['before']
    assert identities(current) == row['after']
    for alg, prior in row['before'].items():
        assert overview_predicate_hash(ROOT, path, prior, alg) == row['after'][alg]
        with pytest.raises(AssertionError):
            overview_predicate_hash(ROOT, path, row['after'][alg], alg)
    with pytest.raises(AssertionError):
        before_overview_predicate_revision(ROOT, path, current+b'\n')

@pytest.mark.parametrize('prefix', PREFIXES)
def test_only_overview_changed_and_readme_shows_same_paper_summary(prefix):
    path = prefix+'lab.yaml'
    raw = (ROOT/path).read_bytes()
    old, new = map(yaml.safe_load, (before_overview_predicate_revision(ROOT, path, raw), raw))
    earlier, overview = (d['sections'].pop('overview') for d in (old, new))
    assert old == new
    assert (ROOT/(prefix+'README.md')).read_text().count(overview)==1

    def values(s):
        # OxygenREC-v2 is a model name rather than a measurement.
        return set(re.findall(r'\d+(?:\.\d+)?%?', s.replace('OxygenREC-v2', '')))
    assert values(earlier) == values(overview) == EXPECTED_NUMBERS[Path(prefix).name]
    assert '著者' in overview
    assert 'Lab' not in overview and '増加。' not in overview

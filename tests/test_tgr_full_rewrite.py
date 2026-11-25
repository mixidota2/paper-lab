"""Keep the TGR paper overview and teaching experiment independent of the body revision."""
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_tgr_full_rewrite, tgr_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/tgr/'


def test_rewrite_keeps_overview_experiment_and_source_identity():
    raw = (ROOT / (P + 'lab.yaml')).read_bytes()
    new = yaml.safe_load(raw)
    old = yaml.safe_load(before_tgr_full_rewrite(ROOT, P + 'lab.yaml', raw))
    for key in old.keys() - {'question', 'summary', 'source_review', 'core_idea', 'sections', 'teaching_figures'}:
        assert new[key] == old[key], key
    for key in old['source_review'].keys() - {'scope'}:
        assert new['source_review'][key] == old['source_review'][key], key
    assert old['sections']['overview'] == new['sections']['overview']
    assert [row['formula'] for row in old['teaching_figures'][2]['steps']] == [
        row['formula'] for row in new['teaching_figures'][2]['steps']]
    claims = ('3.57%', '1.71%', '0.60%', '1.70%', '1.22%', '0.68%', '1.75%', '13.09%')
    assert all(x in new['sections']['evidence'] for x in claims)
    assert '72.9%' in new['sections']['executable_understanding']
    assert '2609.00986v1' in new['sections']['mapping']
    for name, expected in (
        ('run.py', 'e49faef30cce99388f3eeaf201d9cbb43c76d67b'),
        ('results.json', '1567811f1742c397d05fb7ce3ac7da314c1d2482'),
    ):
        preserved = (ROOT / (P + name)).read_bytes()
        assert hashlib.sha1(f'blob {len(preserved)}\0'.encode() + preserved).hexdigest() == expected


def test_review_replays_exact_prior_prose_and_rejects_arbitrary_bytes():
    rows = json.loads((ROOT / 'tests/tgr_full_rewrite_hashes.json').read_text())['files']
    assert rows.keys() == {P + 'lab.yaml', P + 'method.md'}
    for path, row in rows.items():
        raw = (ROOT / path).read_bytes()
        prior = before_tgr_full_rewrite(ROOT, path, raw)
        for alg, digest in (
            ('sha256', lambda b: hashlib.sha256(b).hexdigest()),
            ('blob', lambda b: hashlib.sha1(f'blob {len(b)}\0'.encode() + b).hexdigest()),
        ):
            old, new = digest(prior), digest(raw)
            assert old == row['before_' + alg] and new == row['after_' + alg]
            assert tgr_full_rewrite_hash(ROOT, path, old, alg) == new
            for disallowed in (new, '0' * len(new)):
                with pytest.raises(AssertionError):
                    tgr_full_rewrite_hash(ROOT, path, disallowed, alg)
        with pytest.raises(AssertionError):
            before_tgr_full_rewrite(ROOT, path, raw + b'\n')

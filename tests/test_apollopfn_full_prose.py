"""Only the Apollo teaching note changes in the shared runner."""
import json
from pathlib import Path
import runpy

import pytest

from prose_preservation import before_apollopfn_full_prose, before_rest_full_prose

ROOT = Path(__file__).resolve().parents[1]


def test_shared_runner_replays_every_other_download_exactly(tmp_path):
    path = 'papers/_toy_common.py'
    current = (ROOT / path).read_bytes()
    prior = before_apollopfn_full_prose(ROOT, path, current)
    assert prior != current
    with pytest.raises(AssertionError):
        before_apollopfn_full_prose(ROOT, path, current + b'\n')
    path_old = tmp_path / 'prior.py'
    path_old.write_bytes(prior)
    post_apollo = tmp_path / 'post_apollo.py'
    post_apollo.write_bytes(before_rest_full_prose(ROOT, path, current))
    a, b = map(runpy.run_path, [str(path_old), str(post_apollo)])
    assert a['IDS'] == b['IDS'] and len(a['IDS']) == 11
    for slug in a['IDS']:
        one, two = a['compute'](slug), b['compute'](slug)
        if slug == 'apollopfn':
            assert two == json.loads((ROOT / 'papers' / slug / 'results.json').read_text())
            for x,y in zip(one['explorer']['frames'],two['explorer']['frames'],strict=True):
                assert x.pop('note') != y.pop('note')
        assert one == two, slug

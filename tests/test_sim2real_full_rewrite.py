import hashlib
import json
from pathlib import Path

import pytest

from prose_preservation import before_traffic_value_full_prose, paper_overview_rewrite_hash, sim2real_full_rewrite_hash


ROOT = Path(__file__).resolve().parents[1]
SCOPE = 'papers/sim2real-policy-conditioned-inbound-forecast/'
PATHS = {SCOPE + f for f in ('README.md', 'lab.yaml', 'mapping.md', 'method.md')} | {'paper_lab/batch08.py'}


def hash_content(raw, algorithm):
    if algorithm == 'sha256':
        return hashlib.sha256(raw).hexdigest()
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


@pytest.mark.parametrize('path', sorted(PATHS))
@pytest.mark.parametrize('algorithm', ('sha256', 'blob'))
def test_sim2real_prose_guard_identity(path, algorithm):
    proof = json.loads((ROOT / 'tests/sim2real_full_rewrite_hashes.json').read_text())
    assert proof['base'] == 'f7793bc88ab49a347b43e74a9ff45e77bb6fe5ad'
    assert set(proof['files']) == PATHS
    row = proof['files'][path]
    before = row['before_' + algorithm]
    after = sim2real_full_rewrite_hash(ROOT, path, before, algorithm)
    raw = before_traffic_value_full_prose(ROOT, path, (ROOT / path).read_bytes())
    assert paper_overview_rewrite_hash(ROOT, path, after, algorithm) == hash_content(raw, algorithm)
    assert after != hash_content(raw + b'\n', algorithm)
    wrong = ('0' if before[0] != '0' else '1') + before[1:]
    for value in (wrong, after):
        with pytest.raises(AssertionError):
            sim2real_full_rewrite_hash(ROOT, path, value, algorithm)
    for unchanged in ('README.md', SCOPE + 'run.py', SCOPE + 'results.json'):
        assert sim2real_full_rewrite_hash(ROOT, unchanged, before, algorithm) == before
